import { readFileSync } from "node:fs";
import { resolve } from "node:path";

const root = resolve(import.meta.dirname, "..");
const header = readFileSync(resolve(root, "src/components/Header.tsx"), "utf8");
const styles = readFileSync(resolve(root, "src/styles.css"), "utf8");

const removedHeaderTokens = [
  "header-search",
  "search-input",
  "search-kbd",
  "searchInputRef",
  "header-bell",
  "bell-badge",
  "Notifications",
  "header-avatar",
  "Operator account",
  ">OP<",
];

const checks = removedHeaderTokens.map((token) => ({
  name: `Header no longer renders or references ${token}`,
  pass: !header.includes(token),
}));

checks.push({
  name: "Styles no longer define removed header search/bell/avatar classes",
  pass: !/\.header-(search|bell|avatar)\b|\.search-(input|kbd|icon)\b|\.bell-badge\b/.test(styles),
});

const failures = checks.filter((check) => !check.pass);

if (failures.length > 0) {
  console.error("Header controls regression check failed:");
  for (const failure of failures) {
    console.error(`- ${failure.name}`);
  }
  process.exit(1);
}

console.log("Header controls regression check passed.");
