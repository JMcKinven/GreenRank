import React from "react";

type Props = {
  id?: string;
  label: string;
  value: string;
  placeholder?: string;
  onChange: (value: string) => void;
};

const SearchBar: React.FC<Props> = ({ id = "search", label, value, placeholder, onChange }) => (
  <div>
    <label htmlFor={id}>{label}</label>
    <input
      id={id}
      type="search"
      placeholder={placeholder}
      value={value}
      onChange={(e) => onChange(e.target.value)}
    />
  </div>
);

export default SearchBar;
