const { app, BrowserWindow, ipcMain, shell } = require('electron')
const path = require('path')
const fs = require('fs')
const { spawn, execFileSync } = require('child_process')

const API_URL = 'http://127.0.0.1:8000'
const DEV_URL = 'http://localhost:5173'

function resolveMasDir() {
  if (process.env.ERRORLOGY_MAS_DIR) {
    return path.resolve(process.env.ERRORLOGY_MAS_DIR)
  }
  if (app.isPackaged) {
    const pub = process.env.PUBLIC || 'C:\\Users\\Public'
    return path.join(pub, 'ERRORLOGY_MVP', 'errorlogy-mas')
  }
  return path.join(__dirname, '..', '..', 'errorlogy-mas')
}

const MAS_DIR = resolveMasDir()

let win = null
let apiProcess = null
let apiOwnedByApp = false

function resolvePython() {
  if (process.env.ERRORLOGY_PYTHON) {
    return { cmd: process.env.ERRORLOGY_PYTHON, argsPrefix: [] }
  }

  const candidates = [
    { cmd: 'py', argsPrefix: ['-3'] },
    { cmd: 'python', argsPrefix: [] },
    { cmd: 'python3', argsPrefix: [] },
  ]

  if (process.platform === 'win32') {
    const localAppData = process.env.LOCALAPPDATA || ''
    for (const ver of ['313', '312', '311', '310']) {
      candidates.push({
        cmd: path.join(localAppData, 'Programs', 'Python', `Python${ver}`, 'python.exe'),
        argsPrefix: [],
      })
    }
  }

  for (const candidate of candidates) {
    const { cmd, argsPrefix } = candidate
    if (cmd.includes(path.sep) && !fs.existsSync(cmd)) continue
    try {
      execFileSync(cmd, [...argsPrefix, '-c', 'import uvicorn'], {
        timeout: 8000,
        stdio: 'ignore',
        env: process.env,
      })
      return candidate
    } catch { /* try next */ }
  }

  console.warn('[electron] No Python with uvicorn found — falling back to "python"')
  return { cmd: 'python', argsPrefix: [] }
}

function isAPIUp() {
  const http = require('http')
  return new Promise(resolve => {
    const req = http.get(API_URL + '/api/health', res => {
      res.resume()
      resolve(res.statusCode === 200)
    })
    req.on('error', () => resolve(false))
    req.setTimeout(2000, () => {
      req.destroy()
      resolve(false)
    })
  })
}

async function waitForAPI(retries = 45) {
  for (let i = 0; i < retries; i++) {
    if (await isAPIUp()) {
      console.log('[electron] API ready')
      return true
    }
    await new Promise(r => setTimeout(r, 1000))
  }
  return false
}

function startAPI() {
  const mainPy = path.join(MAS_DIR, 'api', 'main.py')
  if (!fs.existsSync(mainPy)) {
    console.error('[electron] MAS not found — expected api/main.py at:', MAS_DIR)
    console.error('[electron] Set ERRORLOGY_MAS_DIR to your errorlogy-mas folder.')
    return false
  }

  const { cmd, argsPrefix } = resolvePython()
  console.log('[electron] Starting FastAPI backend...')
  console.log('[electron] PYTHON:', cmd, argsPrefix.join(' '), '| MAS_DIR:', MAS_DIR)

  apiProcess = spawn(
    cmd,
    [...argsPrefix, '-m', 'uvicorn', 'api.main:app', '--host', '127.0.0.1', '--port', '8000'],
    {
      cwd: MAS_DIR,
      env: { ...process.env, PYTHONIOENCODING: 'utf-8' },
      stdio: ['ignore', 'pipe', 'pipe'],
      windowsHide: true,
    },
  )
  apiOwnedByApp = true

  apiProcess.stdout.on('data', d => console.log('[api]', d.toString().trim()))
  apiProcess.stderr.on('data', d => process.stderr.write('[api] ' + d.toString()))
  apiProcess.on('error', err => {
    console.error('[electron] Failed to spawn API:', err.message)
    apiProcess = null
    apiOwnedByApp = false
  })
  apiProcess.on('exit', code => {
    console.log('[api] exited', code)
    apiProcess = null
    apiOwnedByApp = false
  })

  return true
}

async function ensureAPI() {
  if (await isAPIUp()) {
    console.log('[electron] API already running on :8000')
    return true
  }

  if (!startAPI()) return false
  return waitForAPI()
}

function stopAPI() {
  if (apiProcess && apiOwnedByApp && !apiProcess.killed) {
    console.log('[electron] Stopping FastAPI child process')
    apiProcess.kill()
  }
  apiProcess = null
  apiOwnedByApp = false
}

function isDevServerUp() {
  const http = require('http')
  return new Promise(resolve => {
    const req = http.get(DEV_URL, res => {
      res.resume()
      resolve(res.statusCode === 200)
    })
    req.on('error', () => resolve(false))
    req.setTimeout(1500, () => {
      req.destroy()
      resolve(false)
    })
  })
}

async function loadRenderer() {
  const distIndex = path.join(__dirname, '..', 'dist', 'index.html')
  const preferDev = !app.isPackaged && process.env.ERRORLOGY_GUI_DIST !== '1'
  const viteUp = preferDev && await isDevServerUp()

  if (viteUp) {
    console.log('[electron] Vite dev server:', DEV_URL)
    await win.loadURL(DEV_URL)
    return
  }

  if (preferDev) {
    console.log('[electron] Vite not running — loading dist/. Start `npm run dev:vite` for live reload.')
  } else {
    console.log('[electron] Packaged build — loading bundled dist')
  }
  await win.loadFile(distIndex)
}

function createWindow() {
  win = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1100,
    minHeight: 700,
    backgroundColor: '#0f172a',
    titleBarStyle: 'hidden',
    frame: false,
    webPreferences: {
      preload: path.join(__dirname, 'preload.cjs'),
      contextIsolation: true,
      nodeIntegration: false,
    },
    icon: path.join(__dirname, '..', 'public', 'icon.png'),
  })

  loadRenderer().catch(err => console.error('[electron] Failed to load UI:', err))
}

app.whenReady().then(async () => {
  const ready = await ensureAPI()
  if (!ready) {
    console.warn('[electron] API not ready — UI will show offline until backend starts')
  }
  createWindow()

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow()
  })
})

app.on('before-quit', stopAPI)

app.on('window-all-closed', () => {
  stopAPI()
  if (process.platform !== 'darwin') app.quit()
})

// IPC: window controls
ipcMain.on('window:minimize', () => win?.minimize())
ipcMain.on('window:maximize', () => win?.isMaximized() ? win.unmaximize() : win.maximize())
ipcMain.on('window:close', () => win?.close())
ipcMain.handle('window:isMaximized', () => win?.isMaximized())
ipcMain.on('shell:openExternal', (_, url) => shell.openExternal(url))
