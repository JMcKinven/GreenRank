import React, { useMemo, useEffect, useState } from "react";
import "./App.css";

import CompanyList from "./components/Leaderboard";
import NewsFeed from "./components/NewsFeed";

import { Toggle } from "./components/Toggle";
import SearchBar from "./components/Search";
import SortDropdown, { SortOption } from "./components/Sort";
import FilterDropdown, { Option } from "./components/Filter";

import useLocalStorage from "use-local-storage";

function App() {
  const preference = window.matchMedia("(prefers-color-scheme: dark)").matches;
  const [isDark, setIsDark] = useLocalStorage("isDark", preference);

  useEffect(() => {
    document.documentElement.setAttribute(
      "data-theme",
      isDark ? "dark" : "light"
    );
  }, [isDark]);

  // UI state
  const [search, setSearch] = useState("");
  const [sort, setSort] = useState("rank_desc");
  const [filter, setFilter] = useState("all");

  const sortOptions: SortOption[] = useMemo(
    () => [
      { value: "rank_desc", label: "Highest rank → Lowest" },
      { value: "rank_asc", label: "Lowest rank → Highest" },
      { value: "name_asc", label: "A → Z" },
      { value: "name_desc", label: "Z → A" },
    ],
    []
  );

  const filterOptions: Option[] = useMemo(
    () => [
      { value: "all", label: "All sectors" },
      { value: "finance", label: "Finance" },
      { value: "retail", label: "Retail" },
      { value: "fashion", label: "Fashion" },
      { value: "heavy industry", label: "Heavy Industry" },
      { value: "construction", label: "Construction" },
    ],
    []
  );

  return (
    <div className="App" data-theme={isDark ? "dark" : "light"}>
      <div className="App-shell">
        <h1>GreenRank Dashboard</h1>

        <div className="dashboard-layout">
          <SearchBar
            id="searchBar"
            label="Search by company"
            value={search}
            placeholder="Type a company name…"
            onChange={setSearch}
          />

          <div className="dashboard-controls">
            <SortDropdown
              id="sortDropdown"
              label="Sort"
              value={sort}
              options={sortOptions}
              onChange={setSort}
            />
            <FilterDropdown
              id="filterDropdown"
              label="Filter"
              value={filter}
              options={filterOptions}
              onChange={setFilter}
            />
            <Toggle
              isChecked={isDark}
              handleChange={() => setIsDark((prev) => !prev)}
            />
          </div>
        </div>

        {/* ----- NEW 2-column layout ----- */}
        <div className="dashboard-row">
          <div className="left-column">
            <CompanyList search={search} sort={sort} filter={filter} />
          </div>

          <div className="right-column">
            <NewsFeed />
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
