import { spawn } from 'node:child_process';
import { existsSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

// Keep the old Node entry point working; the API itself lives in main.py.
const backendDir = dirname(fileURLToPath(import.meta.url));
const localPython = join(backendDir, 'venv', 'bin', 'python');
const python = process.env.PYTHON || (existsSync(localPython) ? localPython : 'python3');
const child = spawn(python, ['-B', 'main.py', ...process.argv.slice(2)], {
  cwd: backendDir,
  stdio: 'inherit',
});

child.on('error', (error) => {
  console.error(`Could not start Python backend: ${error.message}`);
  process.exitCode = 1;
});
child.on('exit', (code, signal) => {
  process.exitCode = code ?? (signal ? 1 : 0);
});
for (const signal of ['SIGINT', 'SIGTERM']) {
  process.on(signal, () => child.kill(signal));
}
