import React from "react";
import { Routes } from "react-router";
import { Route } from "react-router";
import { BrowserRouter } from "react-router";
import Home from "./pages/Home/Home";
import Prompt from "./pages/Prompt/Prompt";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />}></Route>
        <Route path="/prompt" element={<Prompt />}></Route>
      </Routes>
    </BrowserRouter>
  );
}
