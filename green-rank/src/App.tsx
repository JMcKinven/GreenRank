import React, { useState } from 'react';
import './App.css';
import CompanyList from './components/leaderboard';
import { Toggle } from './components/Toggle';
import useLocalStorage from 'use-local-storage';

function App() {
    const preference = window.matchMedia("(prefer-color-scheme: dark)").matches;
    const [isDark, setIsDark] = useLocalStorage("isDark", preference);



    return (
        <div className="App" data-theme={isDark ? "dark" : "light"}>
            <Toggle
                isChecked={isDark}
                handleChange={() => setIsDark(!isDark) }
            />
                <h1>GreenRank Dashboard</h1>
                <CompanyList /> {}
        </div>
    );
}

export default App;
