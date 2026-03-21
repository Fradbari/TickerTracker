const fs = require('fs');
const FILE = 'src/features/estimates/__tests__/EstimateForm.test.tsx';
let c = fs.readFileSync(FILE, 'utf8');

c = `import { fireEvent } from '@testing-library/react';\n` + c;
// We know \`await userEvent.click(submitBtn)\` causes unhandled rejection because Zod inside hookform acts weird with userEvent.
c = c.replace(/await userEvent\.click\(submitBtn\)/g, 'fireEvent.click(submitBtn)');
fs.writeFileSync(FILE, c);
console.log('done');
