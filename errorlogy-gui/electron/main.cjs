const { app, BrowserWindow, ipcMain, shell } = require('electron')
const path = require('path')
const fs = require('fs')
const os = require('os')
const { spawn, execFileSync, execSync } = require('child_process')

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
let logStream = null

function getLogDir() {
  const localAppData = process.env.LOCALAPPDATA || path.join(os.homedir(), 'AppData', 'Local')
  return path.join(localAppData, 'errorlogy-gui')
}

function getApiStartupLogPath() {
  return path.join(getLogDir(), 'api-startup.log')
}

function initApiLog() {
  if (logStream) return
  try {
    const logDir = getLogDir()
    fs.mkdirSync(logDir, { recursive: true })
    logStream = fs.createWriteStream(getApiStartupLogPath(), { flags: 'a' })
    apiLog(`\n=== Errorlogy API startup ${new Date().toISOString()} ===`)
    apiLog(`packaged=${app.isPackaged} pid=${process.pid}`)
    apiLog(`MAS_DIR=${MAS_DIR}`)
  } catch (err) {
    console.error('[electron] Failed to init api-startup.log:', err.message)
  }
}

function apiLog(msg) {
  const stamped = `[${new Date().toISOString()}] ${msg}`
  console.log('[electron]', msg)
  if (logStream && !logStream.destroyed) {
    logStream.write(stamped + '\n')
  }
}

function pythonTestCode() {
  const mainPy = path.join(MAS_DIR, 'api', 'main.py')
  return fs.existsSync(mainPy) ? 'import api.main' : 'import uvicorn'
}

function resolvePython() {
  if (process.env.ERRORLOGY_PYTHON) {
    return { cmd: process.env.ERRORLOGY_PYTHON, argsPrefix: [], shell: false }
  }

  const useShell = process.platform === 'win32'
  const testCode = pythonTestCode()
  const candidates = []

  // Absolute paths first — desktop shortcuts often strip user PATH (no py/python).
  if (process.platform === 'win32') {
    const localAppData = process.env.LOCALAPPDATA || ''
    for (const ver of ['312', '313', '311', '310']) {
      candidates.push({
        cmd: path.join(localAppData, 'Programs', 'Python', `Python${ver}`, 'python.exe'),
        argsPrefix: [],
        shell: false,
      })
    }
  }

  candidates.push(
    { cmd: 'py', argsPrefix: ['-3.12'], shell: useShell },
    { cmd: 'py', argsPrefix: ['-3'], shell: useShell },
    // Generic python last — often Hermes/conda venv with uvicorn but without MAS deps.
    { cmd: 'python', argsPrefix: [], shell: false },
    { cmd: 'python3', argsPrefix: [], shell: false },
  )

  for (const candidate of candidates) {
    const { cmd, argsPrefix, shell } = candidate
    if (cmd.includes(path.sep) && !fs.existsSync(cmd)) {
      apiLog(`resolvePython: skip missing ${cmd}`)
      continue
    }
    try {
      if (shell) {
        const parts = [cmd, ...argsPrefix, '-c', testCode].map(p =>
          /[\s"]/.test(p) ? `"${p.replace(/"/g, '\\"')}"` : p,
        )
        execSync(parts.join(' '), {
          timeout: 15000,
          stdio: 'ignore',
          env: process.env,
          shell: true,
          cwd: MAS_DIR,
        })
      } else {
        execFileSync(cmd, [...argsPrefix, '-c', testCode], {
          timeout: 15000,
          stdio: 'ignore',
          env: process.env,
          cwd: MAS_DIR,
        })
      }
      apiLog(`resolvePython: selected ${cmd} ${argsPrefix.join(' ')} shell=${shell} test=${testCode}`)
      return candidate
    } catch (err) {
      apiLog(`resolvePython: failed ${cmd} ${argsPrefix.join(' ')}: ${err.message}`)
    }
  }

  const fallback312 = path.join(
    process.env.LOCALAPPDATA || path.join(os.homedir(), 'AppData', 'Local'),
    'Programs', 'Python', 'Python312', 'python.exe',
  )
  if (fs.existsSync(fallback312)) {
    apiLog(`resolvePython: fallback explicit ${fallback312}`)
    return { cmd: fallback312, argsPrefix: [], shell: false }
  }

  apiLog('resolvePython: fallback py -3.12 (shell)')
  return { cmd: 'py', argsPrefix: ['-3.12'], shell: useShell }
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

async function waitForAPI(retries = 60) {
  apiLog(`waitForAPI: up to ${retries} attempts`)
  for (let i = 0; i < retries; i++) {
    if (await isAPIUp()) {
      apiLog(`API ready after ${i + 1} attempt(s)`)
      return true
    }
    await new Promise(r => setTimeout(r, 1000))
  }
  apiLog(`API not ready after ${retries} attempts`)
  return false
}

function startAPI() {
  initApiLog()

  apiLog(`MAS_DIR exists=${fs.existsSync(MAS_DIR)} path=${MAS_DIR}`)

  if (!fs.existsSync(MAS_DIR)) {
    apiLog(`ERROR: MAS_DIR does not exist: ${MAS_DIR}`)
    apiLog('Set ERRORLOGY_MAS_DIR to your errorlogy-mas folder.')
    return false
  }

  const mainPy = path.join(MAS_DIR, 'api', 'main.py')
  apiLog(`main.py path=${mainPy} exists=${fs.existsSync(mainPy)}`)

  if (!fs.existsSync(mainPy)) {
    apiLog(`ERROR: api/main.py not found — expected at ${mainPy}`)
    apiLog('Set ERRORLOGY_MAS_DIR to your errorlogy-mas folder.')
    return false
  }

  const { cmd, argsPrefix, shell } = resolvePython()
  const spawnArgs = [...argsPrefix, '-m', 'uvicorn', 'api.main:app', '--host', '127.0.0.1', '--port', '8000']

  apiLog(`spawn: cmd=${cmd} args=${spawnArgs.join(' ')} cwd=${MAS_DIR} shell=${shell}`)

  const spawnOpts = {
    cwd: MAS_DIR,
    env: { ...process.env, PYTHONIOENCODING: 'utf-8' },
    stdio: ['ignore', 'pipe', 'pipe'],
    windowsHide: true,
  }
  if (shell) spawnOpts.shell = true

  try {
    apiProcess = spawn(cmd, spawnArgs, spawnOpts)
  } catch (err) {
    apiLog(`spawn threw: ${err.message}`)
    return false
  }

  apiOwnedByApp = true

  apiProcess.stdout.on('data', d => {
    const text = d.toString().trim()
    if (text) apiLog(`[api stdout] ${text}`)
  })
  apiProcess.stderr.on('data', d => {
    const text = d.toString().trim()
    if (text) apiLog(`[api stderr] ${text}`)
  })
  apiProcess.on('error', err => {
    apiLog(`spawn error event: ${err.message}`)
    apiProcess = null
    apiOwnedByApp = false
  })
  apiProcess.on('exit', (code, signal) => {
    apiLog(`api process exited code=${code} signal=${signal ?? 'none'}`)
    apiProcess = null
    apiOwnedByApp = false
  })

  apiLog(`spawn ok pid=${apiProcess.pid ?? 'unknown'}`)
  return true
}

async function ensureAPI() {
  initApiLog()
  apiLog('ensureAPI: checking if API already up')

  if (await isAPIUp()) {
    apiLog('API already running on :8000')
    return true
  }

  if (!startAPI()) return false
  return waitForAPI()
}

function stopAPI() {
  if (apiProcess && apiOwnedByApp && !apiProcess.killed) {
    apiLog('Stopping FastAPI child process')
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
    apiLog('API not ready — UI will show offline until backend starts')
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
ipcMain.handle('app:getApiStartupLogPath', () => getApiStartupLogPath())
