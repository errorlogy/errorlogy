const { contextBridge, ipcRenderer } = require('electron')

contextBridge.exposeInMainWorld('electron', {
  minimize:     () => ipcRenderer.send('window:minimize'),
  maximize:     () => ipcRenderer.send('window:maximize'),
  close:        () => ipcRenderer.send('window:close'),
  isMaximized:  () => ipcRenderer.invoke('window:isMaximized'),
  openExternal: (url) => ipcRenderer.send('shell:openExternal', url),
  getApiStartupLogPath: () => ipcRenderer.invoke('app:getApiStartupLogPath'),
})
