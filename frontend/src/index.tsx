import ReactDOM from "react-dom/client";
import App from "./App";

import "@gravity-ui/uikit/styles/fonts.css";
import "@gravity-ui/uikit/styles/styles.css";
import { ThemeProvider, Toaster, ToasterProvider } from "@gravity-ui/uikit";

const root = ReactDOM.createRoot(
  document.getElementById("root") as HTMLElement
);
const toaster = new Toaster();

root.render(
  <ThemeProvider theme="light">
    <ToasterProvider toaster={toaster}>
      <App />
    </ToasterProvider>
  </ThemeProvider>
);
