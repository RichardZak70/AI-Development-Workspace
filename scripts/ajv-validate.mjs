#!/usr/bin/env node
import { readFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

import Ajv2020 from 'ajv/dist/2020.js';
import addFormats from 'ajv-formats';
import yaml from 'js-yaml';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(__dirname, '..');

const files = [
  {
    label: 'models',
    schema: 'schemas/models.schema.json',
    data: 'templates/config/models.yaml'
  },
  {
    label: 'prompts',
    schema: 'schemas/prompts.schema.json',
    data: 'templates/config/prompts.yaml'
  }
];

const ajv = new Ajv2020({ strict: false, allErrors: true });
addFormats(ajv);

let hasErrors = false;

for (const { label, schema, data } of files) {
  const schemaPath = path.join(repoRoot, schema);
  const dataPath = path.join(repoRoot, data);

  const schemaContent = await readFile(schemaPath, 'utf-8');
  const schemaJson = JSON.parse(schemaContent);

  const dataContent = await readFile(dataPath, 'utf-8');
  const parsedData = yaml.load(dataContent) ?? {};

  const validate = ajv.compile(schemaJson);
  const valid = validate(parsedData);

  if (!valid) {
    hasErrors = true;
    console.error(`❌ ${label} config failed schema validation: ${dataPath}`);
    for (const err of validate.errors ?? []) {
      const location = err.instancePath || '<root>';
      console.error(`  - ${location}: ${err.message}`);
    }
  } else {
    console.log(`✅ ${label} config matches ${schema}`);
  }
}

if (hasErrors) {
  process.exitCode = 1;
}
