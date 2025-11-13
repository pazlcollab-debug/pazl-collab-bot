import fs from "fs";
import path from "path";
import chalk from "chalk"; // для красивого цветного вывода

// пути
const envPath = path.resolve("../.env");
const logPath = path.resolve("./ngrok.log");

// 🕒 ждем, пока ngrok запишет URL
function waitForNgrokUrl(timeout = 15000) {
  return new Promise((resolve, reject) => {
    const start = Date.now();

    const check = () => {
      if (!fs.existsSync(logPath)) {
        if (Date.now() - start > timeout) return reject("ngrok.log не найден");
        return setTimeout(check, 500);
      }

      const logData = fs.readFileSync(logPath, "utf8");
      const match = logData.match(/Forwarding\s+(https:\/\/[^\s]+)/);

      if (match) return resolve(match[1]);
      if (Date.now() - start > timeout) return reject("URL не найден в ngrok.log");
      setTimeout(check, 500);
    };

    check();
  });
}

(async () => {
  try {
    console.log(chalk.cyan("⏳ Ожидание запуска ngrok..."));
    const newUrl = await waitForNgrokUrl();

    let env = fs.existsSync(envPath) ? fs.readFileSync(envPath, "utf8") : "";
    if (env.includes("WEBAPP_URL=")) {
      env = env.replace(/WEBAPP_URL=.*/g, `WEBAPP_URL=${newUrl}`);
    } else {
      env += `\nWEBAPP_URL=${newUrl}\n`;
    }

    fs.writeFileSync(envPath, env);

    console.log(chalk.greenBright(`✅ WEBAPP_URL обновлён:`));
    console.log(chalk.bold.blue(`   ${newUrl}\n`));
    console.log(chalk.gray("Теперь Mini App откроется в Telegram по актуальной ссылке 🌐"));
  } catch (err) {
    console.error(chalk.red("⚠️ Ошибка при обновлении WEBAPP_URL:"), err);
  }
})();
