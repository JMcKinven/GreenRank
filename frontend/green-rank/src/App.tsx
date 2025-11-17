import React, { useMemo } from 'react';
import './App.css';
import CompanyList from './components/Leaderboard';
import { Toggle } from './components/Toggle';
import useLocalStorage from 'use-local-storage';
import SearchBar from './components/Search';
import SortDropdown, { SortOption } from './components/Sort';
import FilterDropdown, { Option } from './components/Filter';

function App() {
  const preference = window.matchMedia('(prefer-color-scheme: dark)').matches;
  const [isDark, setIsDark] = useLocalStorage('isDark', preference);

  // UI state
  const [search, setSearch] = React.useState<string>('');
  const [sort, setSort] = React.useState<string>('rank_desc'); // default: highest rank to lowest
  const [filter, setFilter] = React.useState<string>('all');

  const sortOptions: SortOption[] = useMemo(
    () => [
      { value: 'rank_desc', label: 'Highest rank → Lowest' }, // score DESC
      { value: 'rank_asc', label: 'Lowest rank → Highest' },  // score ASC
      { value: 'name_asc', label: 'A → Z' },
      { value: 'name_desc', label: 'Z → A' },
    ],
    []
  );

  const filterOptions: Option[] = useMemo(
    () => [
      { value: 'all', label: 'All sectors' },
      { value: 'finance', label: 'Finance' },
      { value: 'retail', label: 'Retail' },
      { value: 'fashion', label: 'Fashion' },
      { value: 'heavy industry', label: 'Heavy Industry' },
      { value: 'construction', label: 'Construction' },
    ],
    []
  );

  return (
    <div className="App" data-theme={isDark ? 'dark' : 'light'}>
      <Toggle isChecked={isDark} handleChange={() => setIsDark(!isDark)} />
      <h1>GreenRank Dashboard</h1>

      <div style={{ display: 'grid', gap: '0.75rem', gridTemplateColumns: '1fr', maxWidth: 900, margin: '0 auto' }}>
        <SearchBar
          id="searchBar"
          label="Search by company"
          value={search}
          placeholder="Type a company name…"
          onChange={setSearch}
        />
        <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
          <SortDropdown id="sortDropdown" label="Sort" value={sort} options={sortOptions} onChange={setSort} />
          <FilterDropdown id="filterDropdown" label="Filter" value={filter} options={filterOptions} onChange={setFilter} />
        </div>
      </div>

      <CompanyList search={search} sort={sort} filter={filter} />
    </div>
  );
}

export default App;
