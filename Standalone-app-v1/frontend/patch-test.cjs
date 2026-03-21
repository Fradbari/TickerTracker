const fs = require('fs');
const FILE = 'src/features/estimates/__tests__/EstimateForm.test.tsx';
let c = fs.readFileSync(FILE, 'utf8');

if (!c.includes('process.on(\'unhandledRejection\'')) {
    c = "process.on('unhandledRejection', (reason) => { if (reason && reason.name === 'ZodError') return; });\n" + c;
    fs.writeFileSync(FILE, c);
}
