// === CONFIGURAZIONE ===
const FOLDER_ID = '1PfvwmDwznqMWftgygafto0-iJpV_x8sA'; // ID cartella Drive

// === HELPER: Logging Debug con Auto-cleanup per spazio ===
function logDebug(message, level = 'info') {
  const folder = DriveApp.getFolderById(FOLDER_ID);
  const logFileName = 'debug_logs.json';
  let logFile;
  const files = folder.getFilesByName(logFileName);
  if (files.hasNext()) {
    logFile = files.next();
  } else {
    logFile = folder.createFile(logFileName, '[]', MimeType.PLAIN_TEXT);
  }
  
  const currentLogs = JSON.parse(logFile.getBlob().getDataAsString() || '[]');
  const logEntry = {
    timestamp: new Date().toISOString(),
    level: level,
    message: message
  };
  currentLogs.push(logEntry);
  
  // Pulisci i log se il file supera 10MB
  const estimatedSize = JSON.stringify(currentLogs).length;
  const MAX_SIZE = 10 * 1024 * 1024; // 10MB
  
  if (estimatedSize > MAX_SIZE && currentLogs.length > 20) {
    // Elimina i 20 log più vecchi
    currentLogs.splice(0, 20);
  } else if (currentLogs.length > 1000) {
    // Mantieni solo gli ultimi 1000 log (fallback)
    currentLogs.splice(0, currentLogs.length - 1000);
  }
  
  logFile.setContent(JSON.stringify(currentLogs, null, 2));
}

// === HELPER: Genera header CSV espanso (120+ colonne) ===
function getCSVHeaders() {
  const headers = [
    // Base data (8 colonne)
    'timestamp', 'date', 'open', 'high', 'low', 'close', 'adjClose', 'volume',
    
    // Calendar events (7 colonne)
    'earningsDate', 'earningsAverage', 'earningsLow', 'earningsHigh', 'revenueAverage', 'exDividendDate', 'dividendDate',
    
    // Recommendation single (5 colonne) - retrocompatibilità
    'strongBuy', 'buy', 'hold', 'sell', 'strongSell',
    
    // Earnings single (5 colonne) - retrocompatibilità
    'lastQuarterDate', 'lastQuarterActual', 'lastQuarterEstimate', 'lastQuarterRevenue', 'lastQuarterEarnings',
    
    // Trend single (4 colonne) - retrocompatibilità
    'growthEstimate', 'earningsEstimateAvg', 'revenueEstimateAvg', 'numberOfAnalysts'
  ];
  
  // Recommendation Trend Full (4 mesi x 5 valori = 20 colonne)
  for (let i = 0; i < 4; i++) {
    headers.push(
      `rec_m${i}_strongBuy`, `rec_m${i}_buy`, `rec_m${i}_hold`, `rec_m${i}_sell`, `rec_m${i}_strongSell`
    );
  }
  
  // Earnings History Full (8 trimestri x 5 valori = 40 colonne)
  for (let i = 0; i < 8; i++) {
    headers.push(
      `earn_q${i}_date`, `earn_q${i}_actual`, `earn_q${i}_estimate`, `earn_q${i}_revenue`, `earn_q${i}_earnings`
    );
  }
  
  // Earnings Trend Full (4 periodi x 4 valori = 16 colonne)
  const trendPeriods = ['0q', '+1q', '0y', '+1y'];
  for (let i = 0; i < 4; i++) {
    const period = trendPeriods[i];
    headers.push(
      `trend_${period}_growth`, `trend_${period}_earnings`, `trend_${period}_revenue`, `trend_${period}_analysts`
    );
  }
  
  return headers;
}

// === HELPER: Conta colonne nel CSV ===
function getColumnCount(csvContent) {
  const lines = csvContent.split('\n').filter(line => line.trim() !== '');
  if (lines.length === 0) return 0;
  return lines[0].split(',').length;
}

// === HELPER: Migra CSV da 30 a 120+ colonne ===
function migrateCSVIfNeeded(csvContent) {
  const lines = csvContent.split('\n').filter(line => line.trim() !== '');
  if (lines.length === 0) return csvContent;
  
  const currentColumnCount = lines[0].split(',').length;
  const newHeaders = getCSVHeaders();
  const newColumnCount = newHeaders.length;
  
  // Se già ha il numero giusto di colonne, non fare nulla
  if (currentColumnCount >= newColumnCount - 5) {
    return csvContent;
  }
  
  logDebug(`CSV Migration: ${currentColumnCount} → ${newColumnCount} colonne`, 'info');
  
  // Estrai header e righe
  const oldHeader = lines[0];
  const oldRows = lines.slice(1);
  
  // Crea nuova versione con colonne vuote aggiunte
  const migratedRows = oldRows.map(row => {
    const columns = row.split(',');
    // Aggiungi colonne vuote per riempire fino al nuovo conteggio
    while (columns.length < newColumnCount) {
      columns.push('');
    }
    return columns.slice(0, newColumnCount).join(',');
  });
  
  // Ricostruisci CSV con nuovo header
  const newCSVContent = newHeaders.join(',') + '\n' + migratedRows.join('\n') + '\n';
  return newCSVContent;
}

// === HELPER: Trova o crea file storico CSV ===
function getOrCreateHistoryFile(folder, ticker) {
  const fileName = `History_${ticker}.csv`;
  const files = folder.getFilesByName(fileName);
  
  if (files.hasNext()) {
    return files.next();
  }
  
  // Crea file CSV con header espanso
  const headers = getCSVHeaders();
  
  return folder.createFile(fileName, headers.join(',') + '\n', MimeType.PLAIN_TEXT);
}


// === SALVATAGGIO (POST) ===
function doPost(e) {
  try {
    const data = JSON.parse(e.postData.contents);
    const folder = DriveApp.getFolderById(FOLDER_ID);
    
    const action = data.action || 'backup';
    
    // === LOG DEBUG (dal client HTML) ===
    if (action === 'logDebug') {
      const message = data.message || '';
      const level = data.level || 'info';
      logDebug(message, level);
      return ContentService.createTextOutput(JSON.stringify({
        status: 'success',
        action: 'logDebug',
        timestamp: new Date().toISOString()
      })).setMimeType(ContentService.MimeType.JSON);
    }
    
    // === APPEND HISTORY (singolo ticker) ===
    if (action === 'appendHistory') {
      const ticker = data.ticker;
      const rows = data.rows;
      
      if (!ticker || !rows || rows.length === 0) {
        return ContentService.createTextOutput(JSON.stringify({
          status: 'error',
          message: 'Ticker e rows richiesti'
        })).setMimeType(ContentService.MimeType.JSON);
      }
      
      const file = getOrCreateHistoryFile(folder, ticker);
      let currentContent = file.getBlob().getDataAsString();
      
      // === MIGRAZIONE CSV SE NECESSARIO ===
      currentContent = migrateCSVIfNeeded(currentContent);
      
      const lines = currentContent.split('\n').filter(line => line.trim() !== '');
      
      const header = lines[0];
      const existingRows = lines.slice(1);
      
      const rowsByDate = {};
      existingRows.forEach(row => {
        const columns = row.split(',');
        const dateCol = columns[1];
        if (dateCol) {
          rowsByDate[dateCol] = row;
        }
      });
      
      let updatedCount = 0;
      let addedCount = 0;
      
      rows.forEach(newRow => {
        const columns = newRow.split(',');
        const dateCol = columns[1];
        
        if (dateCol) {
          if (rowsByDate[dateCol]) {
            rowsByDate[dateCol] = newRow;
            updatedCount++;
          } else {
            rowsByDate[dateCol] = newRow;
            addedCount++;
          }
        }
      });
      
      const allDates = Object.keys(rowsByDate).sort();
      const newContent = header + '\n' + allDates.map(d => rowsByDate[d]).join('\n') + '\n';
      file.setContent(newContent);
      
      return ContentService.createTextOutput(JSON.stringify({
        status: 'success',
        action: 'appendHistory',
        ticker: ticker,
        rowsUpdated: updatedCount,
        rowsAdded: addedCount,
        totalRows: allDates.length,
        fileName: `History_${ticker}.csv`,
        timestamp: new Date().toISOString()
      })).setMimeType(ContentService.MimeType.JSON);
    }
    
    // === BULK APPEND HISTORY ===
    if (action === 'bulkAppendHistory') {
      const tickersData = data.tickers;
      const results = {};
      
      for (const ticker in tickersData) {
        const rows = tickersData[ticker];
        if (rows && rows.length > 0) {
          const file = getOrCreateHistoryFile(folder, ticker);
          const currentContent = file.getBlob().getDataAsString();
          const lines = currentContent.split('\n').filter(line => line.trim() !== '');
          
          const header = lines[0];
          const existingRows = lines.slice(1);
          
          const rowsByDate = {};
          existingRows.forEach(row => {
            const columns = row.split(',');
            const dateCol = columns[1];
            if (dateCol) rowsByDate[dateCol] = row;
          });
          
          let updatedCount = 0;
          let addedCount = 0;
          
          rows.forEach(newRow => {
            const columns = newRow.split(',');
            const dateCol = columns[1];
            if (dateCol) {
              if (rowsByDate[dateCol]) {
                rowsByDate[dateCol] = newRow;
                updatedCount++;
              } else {
                rowsByDate[dateCol] = newRow;
                addedCount++;
              }
            }
          });
          
          const allDates = Object.keys(rowsByDate).sort();
          const newContent = header + '\n' + allDates.map(d => rowsByDate[d]).join('\n') + '\n';
          file.setContent(newContent);
          
          results[ticker] = { 
            updated: updatedCount, 
            added: addedCount, 
            total: allDates.length,
            fileName: `History_${ticker}.csv`
          };
        }
      }
      
      return ContentService.createTextOutput(JSON.stringify({
        status: 'success',
        action: 'bulkAppendHistory',
        results: results,
        timestamp: new Date().toISOString()
      })).setMimeType(ContentService.MimeType.JSON);
    }
    
    // === BACKUP STANDARD ===
    const filename = `TickerTracker_${new Date().getTime()}.json`;
    folder.createFile(filename, JSON.stringify(data), MimeType.PLAIN_TEXT);
    
    return ContentService.createTextOutput(JSON.stringify({
      status: 'success',
      action: 'backup',
      filename: filename,
      timestamp: new Date().toISOString()
    })).setMimeType(ContentService.MimeType.JSON);
    
  } catch(error) {
    return ContentService.createTextOutput(JSON.stringify({
      status: 'error',
      message: error.toString()
    })).setMimeType(ContentService.MimeType.JSON);
  }
}

// === HELPER: Proxy Yahoo Finance con Cookie e Crumb ===
function fetchYahooFinance(ticker, modules, paramCookie, paramCrumb) {
  modules = modules || 'assetProfile';
  
  // Verifica che abbiamo cookie e crumb dai parametri
  if (!paramCookie || !paramCrumb || paramCookie === '' || paramCrumb === '') {
    return {
      status: 'error',
      message: 'Cookie e Crumb non forniti. Vai in Settings dell\'app per inserirli.',
      needsRefresh: true
    };
  }
  
  // URL-encoding corretto
  const encodedTicker = encodeURIComponent(ticker);
  const encodedModules = encodeURIComponent(modules);
  const encodedCrumb = encodeURIComponent(paramCrumb);
  
  const url = `https://query2.finance.yahoo.com/v10/finance/quoteSummary/${encodedTicker}?modules=${encodedModules}&crumb=${encodedCrumb}`;
  
  logDebug(`YAHOO REQUEST: ${ticker} - Modules: ${modules} - URL: ${url}`, 'info');
  
  try {
    const response = UrlFetchApp.fetch(url, {
      method: 'GET',
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'Accept': 'application/json',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://finance.yahoo.com/',
        'Cookie': paramCookie
      },
      muteHttpExceptions: true,
      followRedirects: true
    });
    
    const responseCode = response.getResponseCode();
    const responseText = response.getContentText();
    
    logDebug(`YAHOO RESPONSE: ${ticker} - Code: ${responseCode}`, responseCode === 200 ? 'info' : 'error');
    
    // Se 401/403, i cookie/crumb sono scaduti
    if (responseCode === 401 || responseCode === 403) {
      logDebug(`YAHOO AUTH ERROR: ${ticker} - Cookie/Crumb expired`, 'error');
      return {
        status: 'error',
        code: responseCode,
        message: 'Cookie/Crumb scaduti. Aggiornali in Settings dell\'app.',
        needsRefresh: true
      };
    }
    
    if (responseCode !== 200) {
      logDebug(`YAHOO HTTP ERROR: ${ticker} - ${responseCode}`, 'error');
      return {
        status: 'error',
        code: responseCode,
        message: `Yahoo Finance returned HTTP ${responseCode}`
      };
    }
    
    const data = JSON.parse(responseText);
    
    // DEBUG: Log della struttura completa della risposta
    Logger.log('=== YAHOO RESPONSE STRUCTURE ===');
    Logger.log('Full response (first 3000 chars):');
    Logger.log(JSON.stringify(data, null, 2).substring(0, 3000));
    
    // === SALVA RISPOSTA COMPLETA NEI DEBUG LOG ===
    const responseString = JSON.stringify(data, null, 2);
    logDebug(`YAHOO QUOTESUMMARY RESPONSE (${ticker}) - Modules: ${modules} - Data: ${responseString}`, 'info')
    
    if (data.quoteSummary && data.quoteSummary.result && data.quoteSummary.result[0]) {
      const result = data.quoteSummary.result[0];
      
      logDebug(`YAHOO SUCCESS: ${ticker} - Modules received: ${Object.keys(result).join(', ')}`, 'info');
      
      return {
        status: 'success',
        ticker: ticker,
        data: result
      };
    } else if (data.quoteSummary && data.quoteSummary.error) {
      logDebug(`YAHOO API ERROR: ${ticker} - ${data.quoteSummary.error.description || 'Unknown'}`, 'error');
      return {
        status: 'error',
        message: data.quoteSummary.error.description || 'Unknown Yahoo error'
      };
    } else {
      logDebug(`YAHOO INVALID RESPONSE: ${ticker}`, 'error');
      return {
        status: 'error',
        message: 'Invalid response structure from Yahoo Finance'
      };
    }
    
  } catch (error) {
    logDebug(`YAHOO EXCEPTION: ${ticker} - ${error.toString()}`, 'error');
    return {
      status: 'error',
      message: error.toString()
    };
  }
}

// === HELPER: Proxy Yahoo Finance Chart (OHLC) con Cookie e Crumb ===
function fetchYahooChart(ticker, range, interval, paramCookie, paramCrumb) {
  range = range || '1mo';
  interval = interval || '1d';
  
  // Verifica che abbiamo cookie e crumb dai parametri
  if (!paramCookie || !paramCrumb || paramCookie === '' || paramCrumb === '') {
    return {
      status: 'error',
      message: 'Cookie e Crumb non forniti. Vai in Settings dell\'app per inserirli.',
      needsRefresh: true
    };
  }
  
  // URL-encoding corretto
  const encodedTicker = encodeURIComponent(ticker);
  const encodedCrumb = encodeURIComponent(paramCrumb);
  
  const url = `https://query2.finance.yahoo.com/v8/finance/chart/${encodedTicker}?interval=${interval}&range=${range}&crumb=${encodedCrumb}`;
  
  logDebug(`YAHOO CHART REQUEST: ${ticker} - Range: ${range}, Interval: ${interval} - URL: ${url}`, 'info');
  
  try {
    const response = UrlFetchApp.fetch(url, {
      method: 'GET',
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'Accept': 'application/json',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://finance.yahoo.com/',
        'Cookie': paramCookie
      },
      muteHttpExceptions: true,
      followRedirects: true
    });
    
    const responseCode = response.getResponseCode();
    const responseText = response.getContentText();
    
    logDebug(`YAHOO CHART RESPONSE: ${ticker} - Code: ${responseCode}`, responseCode === 200 ? 'info' : 'error');
    
    // Se 401/403, i cookie/crumb sono scaduti
    if (responseCode === 401 || responseCode === 403) {
      logDebug(`YAHOO CHART AUTH ERROR: ${ticker} - Cookie/Crumb expired`, 'error');
      return {
        status: 'error',
        code: responseCode,
        message: 'Cookie/Crumb scaduti. Aggiornali in Settings dell\'app.',
        needsRefresh: true
      };
    }
    
    if (responseCode !== 200) {
      logDebug(`YAHOO CHART HTTP ERROR: ${ticker} - ${responseCode}`, 'error');
      return {
        status: 'error',
        code: responseCode,
        message: `Yahoo Finance Chart returned HTTP ${responseCode}`
      };
    }
    
    const data = JSON.parse(responseText);
    
    // === SALVA RISPOSTA COMPLETA NEI DEBUG LOG ===
    const responseString = JSON.stringify(data, null, 2);
    logDebug(`YAHOO CHART RESPONSE (${ticker}) - Range: ${range}, Interval: ${interval} - Data: ${responseString}`, 'info')
    
    if (data.chart && data.chart.result && data.chart.result[0]) {
      logDebug(`YAHOO CHART SUCCESS: ${ticker}`, 'info');
      return {
        status: 'success',
        ticker: ticker,
        data: data.chart.result[0]
      };
    } else if (data.chart && data.chart.error) {
      logDebug(`YAHOO CHART API ERROR: ${ticker} - ${data.chart.error.description || 'Unknown'}`, 'error');
      return {
        status: 'error',
        message: data.chart.error.description || 'Unknown Yahoo Chart error'
      };
    } else {
      logDebug(`YAHOO CHART INVALID RESPONSE: ${ticker}`, 'error');
      return {
        status: 'error',
        message: 'Invalid chart response structure from Yahoo Finance'
      };
    }
    
  } catch (error) {
    logDebug(`YAHOO CHART EXCEPTION: ${ticker} - ${error.toString()}`, 'error');
    return {
      status: 'error',
      message: error.toString()
    };
  }
}

// === RIPRISTINO (GET) ===
function doGet(e) {
  try {
    const action = e.parameter.action || 'latest';
    const folder = DriveApp.getFolderById(FOLDER_ID);
    
    // === YAHOO FINANCE PROXY ===
    if (action === 'yahooQuoteSummary') {
      const ticker = e.parameter.ticker;
      
      // ✅ CORRETTO: Richiedi TUTTI i moduli necessari
      const modules = 'assetProfile,calendarEvents,recommendationTrend,earnings,earningsTrend';
      
      const paramCookie = e.parameter.cookie || '';
      const paramCrumb = e.parameter.crumb || '';
      
      if (!ticker) {
        return ContentService.createTextOutput(JSON.stringify({
          status: 'error',
          message: 'Parametro ticker richiesto'
        })).setMimeType(ContentService.MimeType.JSON);
      }
      
      const result = fetchYahooFinance(ticker, modules, paramCookie, paramCrumb);
      return ContentService.createTextOutput(JSON.stringify(result))
        .setMimeType(ContentService.MimeType.JSON);
    }
    
    // === YAHOO FINANCE CHART PROXY ===
    if (action === 'yahooChart') {
      const ticker = e.parameter.ticker;
      const range = e.parameter.range || '1mo';
      const interval = e.parameter.interval || '1d';
      const paramCookie = e.parameter.cookie || '';
      const paramCrumb = e.parameter.crumb || '';
      
      if (!ticker) {
        return ContentService.createTextOutput(JSON.stringify({
          status: 'error',
          message: 'Parametro ticker richiesto'
        })).setMimeType(ContentService.MimeType.JSON);
      }
      
      const result = fetchYahooChart(ticker, range, interval, paramCookie, paramCrumb);
      return ContentService.createTextOutput(JSON.stringify(result))
        .setMimeType(ContentService.MimeType.JSON);
    }
    
    // === LISTA BACKUP ===
    if (action === 'list') {
      const files = folder.getFilesByType(MimeType.PLAIN_TEXT);
      const fileList = [];
      
      while (files.hasNext()) {
        const file = files.next();
        const fileName = file.getName();
        if (fileName.startsWith('TickerTracker_') && fileName.endsWith('.json')) {
          fileList.push({
            id: file.getId(),
            name: fileName,
            date: file.getDateCreated().toISOString(),
            size: file.getSize()
          });
        }
      }
      
      fileList.sort((a, b) => new Date(b.date) - new Date(a.date));
      
      return ContentService.createTextOutput(JSON.stringify({
        status: 'success',
        files: fileList
      })).setMimeType(ContentService.MimeType.JSON);
    }
    
    // === DOWNLOAD BACKUP SPECIFICO ===
    if (action === 'download') {
      const fileId = e.parameter.fileId;
      const file = DriveApp.getFileById(fileId);
      const content = file.getBlob().getDataAsString();
      
      return ContentService.createTextOutput(content)
        .setMimeType(ContentService.MimeType.JSON);
    }
    
    // === SCARICA HISTORY DI UN TICKER ===
    if (action === 'getHistory') {
      const ticker = e.parameter.ticker;
      if (!ticker) {
        return ContentService.createTextOutput(JSON.stringify({
          status: 'error',
          message: 'Parametro ticker richiesto'
        })).setMimeType(ContentService.MimeType.JSON);
      }
      
      const fileName = `History_${ticker}.csv`;
      const files = folder.getFilesByName(fileName);
      
      if (!files.hasNext()) {
        return ContentService.createTextOutput(JSON.stringify({
          status: 'success',
          exists: false,
          content: '',
          ticker: ticker
        })).setMimeType(ContentService.MimeType.JSON);
      }
      
      const file = files.next();
      const content = file.getBlob().getDataAsString();
      
      return ContentService.createTextOutput(JSON.stringify({
        status: 'success',
        exists: true,
        content: content,
        ticker: ticker,
        lastModified: file.getLastUpdated().toISOString()
      })).setMimeType(ContentService.MimeType.JSON);
    }
    
    // === LISTA FILE HISTORY ===
    if (action === 'listHistory') {
      const files = folder.getFiles();
      const historyFiles = [];
      
      while (files.hasNext()) {
        const file = files.next();
        const name = file.getName();
        if (name.startsWith('History_') && name.endsWith('.csv')) {
          const ticker = name.replace('History_', '').replace('.csv', '');
          historyFiles.push({
            ticker: ticker,
            id: file.getId(),
            name: name,
            lastModified: file.getLastUpdated().toISOString(),
            size: file.getSize()
          });
        }
      }
      
      return ContentService.createTextOutput(JSON.stringify({
        status: 'success',
        files: historyFiles
      })).setMimeType(ContentService.MimeType.JSON);
    }
    
    // === GET DEBUG LOGS ===
    if (action === 'logs') {
      const logFileName = 'debug_logs.json';
      const files = folder.getFilesByName(logFileName);
      if (!files.hasNext()) {
        return ContentService.createTextOutput(JSON.stringify({
          status: 'success',
          logs: []
        })).setMimeType(ContentService.MimeType.JSON);
      }
      const logFile = files.next();
      const logs = JSON.parse(logFile.getBlob().getDataAsString() || '[]');
      return ContentService.createTextOutput(JSON.stringify({
        status: 'success',
        logs: logs
      })).setMimeType(ContentService.MimeType.JSON);
    }
    
    // === DEFAULT: ULTIMO BACKUP ===
    const files = folder.getFilesByType(MimeType.PLAIN_TEXT);
    let latestFile = null;
    let latestDate = new Date(0);
    
    while (files.hasNext()) {
      const file = files.next();
      const fileName = file.getName();
      if (fileName.startsWith('TickerTracker_') && fileName.endsWith('.json')) {
        const fileDate = file.getDateCreated();
        if (fileDate > latestDate) {
          latestDate = fileDate;
          latestFile = file;
        }
      }
    }
    
    if (!latestFile) {
      return ContentService.createTextOutput(JSON.stringify({
        status: 'error',
        message: 'Nessun backup trovato'
      })).setMimeType(ContentService.MimeType.JSON);
    }
    
    const content = latestFile.getBlob().getDataAsString();
    return ContentService.createTextOutput(content)
      .setMimeType(ContentService.MimeType.JSON);
    
  } catch(error) {
    return ContentService.createTextOutput(JSON.stringify({
      status: 'error',
      message: error.toString()
    })).setMimeType(ContentService.MimeType.JSON);
  }
}