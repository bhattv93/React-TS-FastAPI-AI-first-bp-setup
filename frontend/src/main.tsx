import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';

import { App } from './App';
import { ConfigErrorScreen } from './components/ConfigErrorScreen';
import './index.css';
import { createQueryClient } from './queryClient';
import { loadConfig } from './utils/config';
import { getErrorMessage } from './utils/errors';

async function bootstrap(): Promise<void> {
  const container = document.getElementById('root');
  if (container === null) {
    throw new Error('Missing #root element');
  }
  const root = createRoot(container);
  try {
    await loadConfig();
  } catch (error) {
    root.render(<ConfigErrorScreen message={getErrorMessage(error)} />);
    return;
  }
  root.render(
    <StrictMode>
      <BrowserRouter>
        <App queryClient={createQueryClient()} />
      </BrowserRouter>
    </StrictMode>,
  );
}

void bootstrap();
