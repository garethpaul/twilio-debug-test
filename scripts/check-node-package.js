'use strict';

const fs = require('fs');
const path = require('path');

const root = path.resolve(__dirname, '..');
const packageJson = JSON.parse(fs.readFileSync(path.join(root, 'package.json'), 'utf8'));
const packageLock = JSON.parse(fs.readFileSync(path.join(root, 'package-lock.json'), 'utf8'));

function requireContract(condition, message) {
  if (!condition) {
    throw new Error(message);
  }
}

requireContract(packageJson.private === true, 'package.json must remain private');
requireContract(packageJson.engines.node === '>=20.0.0', 'package.json must require Node 20 or newer');
requireContract(
  packageJson.dependencies && packageJson.dependencies.twilio === '6.0.2',
  'package.json must pin twilio exactly to 6.0.2'
);
requireContract(!packageJson.devDependencies, 'package.json must not add unneeded development dependencies');
requireContract(packageLock.lockfileVersion === 3, 'package-lock.json must use lockfileVersion 3');
requireContract(
  packageLock.packages && packageLock.packages[''] && packageLock.packages[''].dependencies.twilio === '6.0.2',
  'package-lock root must pin twilio exactly to 6.0.2'
);
requireContract(
  packageLock.packages['node_modules/twilio'] &&
    packageLock.packages['node_modules/twilio'].version === '6.0.2',
  'package-lock must resolve twilio 6.0.2'
);

console.log('Node package contracts passed');
