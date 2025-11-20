import React from "react";

export type SortOption = { value: string; label: string };

type Props = {
  id?: string;
  label: string;
  value: string;
  options: SortOption[];
  onChange: (value: string) => void;
};

const SortDropdown: React.FC<Props> = ({ id = "sort", label, value, options, onChange }) => (
  <div>
    <label htmlFor={id}>{label}</label>
    <select id={id} value={value} onChange={(e) => onChange(e.target.value)}>
      {options.map((o) => (
        <option key={o.value} value={o.value}>{o.label}</option>
      ))}
    </select>
  </div>
);

export default SortDropdown;
