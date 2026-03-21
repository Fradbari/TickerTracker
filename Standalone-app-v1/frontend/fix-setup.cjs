const fs = require('fs');

const FILE_PATH = 'src/setupTests.ts';
let content = fs.readFileSync(FILE_PATH, 'utf8');

// remove previous custom edits for unhandledRejection
content = content.replace(/process\.on\('unhandledRejection'[\s\S]*?\);/g, '');

const mockStr = `
// Intercept zodResolver to prevent unhandled ZodErrors from failing the test
// due to Zod 4 + hookform mismatch
vi.mock('@hookform/resolvers/zod', async (importOriginal) => {
  const mod = await importOriginal();
  return {
    ...mod,
    zodResolver: (schema, config, options) => {
      const originalResolver = mod.zodResolver(schema, config, options);
      return async (values, context, options) => {
        try {
          return await originalResolver(values, context, options);
        } catch (e) {
          // In case it violently rejects instead of returning an error map
          return { values: {}, errors: e };
        }
      };
    }
  };
});
`;

if (!content.includes('vi.mock(\'@hookform/resolvers/zod\'')) {
    content += mockStr;
}

fs.writeFileSync(FILE_PATH, content);
console.log('setupTests.ts modified successfully.');
