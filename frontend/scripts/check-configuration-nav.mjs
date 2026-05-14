import { readFileSync } from "node:fs";
import { resolve } from "node:path";

const root = resolve(import.meta.dirname, "..");
const app = readFileSync(resolve(root, "src/App.tsx"), "utf8");
const sidebar = readFileSync(resolve(root, "src/components/Sidebar.tsx"), "utf8");

const checks = [
  {
    name: "App imports ConfigurationScreen",
    pass: app.includes('import { ConfigurationScreen } from "./components/ConfigurationScreen";'),
  },
  {
    name: "App renders ConfigurationScreen for the configuration section",
    pass:
      app.includes('activeSection === "configuration"') &&
      app.includes("<ConfigurationScreen />"),
  },
  {
    name: "Sidebar has a Configuration navigation item",
    pass:
      sidebar.includes('activeSection === "configuration"') &&
      sidebar.includes('handleSectionChange("configuration")') &&
      sidebar.includes(">Configuration<"),
  },
];

const failures = checks.filter((check) => !check.pass);

if (failures.length > 0) {
  console.error("Configuration nav regression check failed:");
  for (const failure of failures) {
    console.error(`- ${failure.name}`);
  }
  process.exit(1);
}

console.log("Configuration nav regression check passed.");
