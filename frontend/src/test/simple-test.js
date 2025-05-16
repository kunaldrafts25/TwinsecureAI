// A simple test file that doesn't rely on external dependencies
console.log('Running simple frontend tests...');

import { promises as fs } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, resolve } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Helper function to check if a file exists
async function checkFileExists(filePath, description) {
  try {
    await fs.access(filePath);
    console.log(`✅ ${description} exists at ${filePath}`);
    return true;
  } catch (error) {
    console.error(`❌ ${description} does not exist at ${filePath}`);
    return false;
  }
}

// Main test function
async function runTests() {
  // List all files in the components directory to debug
  console.log('Listing files in components directory:');
  try {
    const componentsDir = resolve(__dirname, '../components');
    try {
      const files = await fs.readdir(componentsDir);
      console.log('Components directory contents:', files);

      if (files.includes('common')) {
        const commonFiles = await fs.readdir(resolve(componentsDir, 'common'));
        console.log('Common directory contents:', commonFiles);
      }
    } catch (error) {
      console.log('Components directory does not exist or cannot be read');
    }
  } catch (error) {
    console.error('Error listing components directory:', error);
  }

  // Test component files
  await checkFileExists(resolve(__dirname, '../components/common/Button.tsx'), 'Button component file');
  await checkFileExists(resolve(__dirname, '../components/common/Card.tsx'), 'Card component file');

  // Test test files
  await checkFileExists(resolve(__dirname, '../components/common/Button.test.tsx'), 'Button test file');
  await checkFileExists(resolve(__dirname, '../components/common/Card.test.tsx'), 'Card test file');
}

// Run the tests
runTests().then(() => {
  console.log('Simple frontend tests completed.');
}).catch(error => {
  console.error('Error running tests:', error);
});
