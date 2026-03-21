const fs = require('fs');
const FILE = 'src/features/estimates/__tests__/EstimateForm.test.tsx';
let c = fs.readFileSync(FILE, 'utf8');

c = c.replace(/await userEvent\.click\(screen\.getByRole\('button', { name: \/crea\/i }\)\);/g, 'fireEvent.click(screen.getByRole(\'button\', { name: /crea/i }));');
c = c.replace(/await userEvent\.click\(submitBtn\);/g, 'fireEvent.click(submitBtn);');

fs.writeFileSync(FILE, c);
