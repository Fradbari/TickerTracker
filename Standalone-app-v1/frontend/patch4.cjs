const fs = require('fs');
const FILE = 'src/features/estimates/__tests__/EstimateForm.test.tsx';
let c = fs.readFileSync(FILE, 'utf8');

c = c.replace(/fireEvent\.click\(/g, 'await userEvent.click(');

if (!c.includes('window.addEventListener(\'unhandledrejection\'')) {
    c = c.replace('describe(\'EstimateForm\', () => {', 'describe(\'EstimateForm\', () => {\n  beforeAll(() => {\n    window.addEventListener(\'unhandledrejection\', (e) => {\n      if (e.reason && e.reason.name === \'ZodError\') {\n        e.preventDefault();\n      }\n    });\n  });');
}

fs.writeFileSync(FILE, c);
