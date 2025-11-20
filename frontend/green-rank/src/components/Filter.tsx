import React from "react";

export type Option = { value: string; label: string };

type Props = {
  id?: string;
  label: string;
  value: string;
  options: Option[];
  onChange: (value: string) => void;
};

const FilterDropdown: React.FC<Props> = ({ id = "filter", label, value, options, onChange }) => (
  <div>
    <label htmlFor={id}>{label}</label>
    <select id={id} value={value} onChange={(e) => onChange(e.target.value)}>
      {options.map((o) => (
        <option key={o.value} value={o.value}>{o.label}</option>
      ))}
    </select>
  </div>
);

export default FilterDropdown;
