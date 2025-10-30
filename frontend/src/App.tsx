import React from "react";
import { Routes } from "react-router";
import { Route } from "react-router";
import { BrowserRouter } from "react-router";
import Home from "./pages/Home/Home";
import styles from "./App.module.css";

export default function App() {
  return (
    <BrowserRouter>
      <div className={styles.appContainer}>
        <div className={styles.imageContainer}>
          <img src="/meme2.webp" alt="" />
        </div>
        <div className={styles.contentContainer}>
          <Routes>
            <Route path="/" element={<Home />}></Route>
          </Routes>
        </div>
      </div>
    </BrowserRouter>
  );
}
