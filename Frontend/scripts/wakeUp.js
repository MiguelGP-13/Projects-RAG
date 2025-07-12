const backendUrl = 'https://rag-backend-miguel.onrender.com';

async function waitForBackend(url, maxRetries = 15, delay = 3000) {
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      const response = await fetch(url);
      if (response.ok) {
        console.log(`Backend ready (attempt ${attempt})`);
        return true;
      } else {
        console.warn(`Health check failed. Status: ${response.status}`);
      }
    } catch (err) {
      console.warn(`Attempt ${attempt}: Backend not ready yet.`);
    }
    await new Promise(resolve => setTimeout(resolve, delay));
  }
  return false;
}

(async function initApp() {
  const statusEl = document.getElementById('status-loading');
  const contentEl = document.getElementById('content-loading');

  if (statusEl) statusEl.textContent = "Waking up backend...";

  const backendIsReady = await waitForBackend(`${backendUrl}/health`);

  if (!backendIsReady) {
    if (statusEl) statusEl.textContent = "Backend is not responding. Try again later.";
    return;
  }

  if (statusEl) statusEl.style.display = 'none';
  if (contentEl) contentEl.style.display = 'block';

  // ✅ Backend is up → now run your app logic (fetch files, load chat, etc)
  // For example:
  loadFiles(); // if you have this function defined elsewhere
})();
