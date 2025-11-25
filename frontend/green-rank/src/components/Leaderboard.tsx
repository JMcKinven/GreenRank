import React, { useState, useEffect, useMemo } from 'react';
import './Leaderboard.css';
import FullScreenModal from './CertificationDisplay';

type Company = {
  id: number;
  name: string;
  sustainability_score: number;
    sector: string;
    global_rank?: number;
};

type Props = {
  search: string; // company name search
  sort: 'rank_desc' | 'rank_asc' | 'name_asc' | 'name_desc'; // 'Best to Worst', 'Worst to Best', 'A-Z', 'Z-A'
  filter: string; // 'all' or sector value
};

type ScoreBand = 'excellent' | 'good' | 'moderate' | 'poor';

function capitalize(str: string): string {
    if (!str) return '';
    return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
}


function getScoreBand(score: number): ScoreBand {
  if (score >= 80) return 'excellent';
  if (score >= 60) return 'good';
  if (score >= 40) return 'moderate';
  return 'poor';
}

function getScoreBandLabel(band: ScoreBand): string {
  switch (band) {
    case 'excellent':
      return 'Excellent';
    case 'good':
      return 'Good';
    case 'moderate':
      return 'Moderate';
    case 'poor':
    default:
      return 'Needs improvement';
  }
}

function CompanyList({ search, sort, filter }: Props) {
  const [companies, setCompanies] = useState<Company[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedCompany, setSelectedCompany] = useState<Company | null>(null);
  const [isModalVisible, setModalVisible] = useState(false);

useEffect(() => {
  let cancelled = false;

  async function fetchCompanies() {
    try {
      const res = await fetch('http://localhost:5000/api/leaderboard');
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();


      const rawList: any[] = Array.isArray(data) ? data : (data?.companies ?? []);


      const normalized: Company[] = rawList.map((r: any) => ({
        id: r.id ?? r.company_id ?? r.companyid ?? 0,
        name: r.name ?? r.company_name ?? '',
        sustainability_score: Number(r.global_score ?? r.sector_score ?? r.sustainability_score ?? r.score ?? 0),
        sector: capitalize(r.sector ?? r.sector_name ?? ''),
      }));

        const ranked = [...normalized].sort(
            (a, b) => (b.sustainability_score ?? 0) - (a.sustainability_score ?? 0)
        );

        ranked.forEach((c, i) => {
            (c as any).global_rank = i + 1;
        });

      if (!cancelled) setCompanies(ranked);
    } catch (err) {
      console.error('Error fetching companies:', err);
      if (!cancelled) setCompanies([]); // don’t crash UI
    } finally {
      if (!cancelled) setLoading(false);
    }
  }

  fetchCompanies();
  return () => { cancelled = true; };
}, []);

  const processed = useMemo(() => {
    let list = [...companies];

    // Filter by sector
    if (filter && filter.toLowerCase() !== 'all') {
      list = list.filter((c) => c.sector.toLowerCase() === filter.toLowerCase());
    }

    // Search by company name
    const q = (search || '').trim().toLowerCase();
    if (q) {
      list = list.filter((c) => c.name.toLowerCase().includes(q));
    }

    // Sort
    switch (sort) {
      case 'rank_asc':
        list.sort((a, b) => (a.sustainability_score ?? 0) - (b.sustainability_score ?? 0));
        break;
      case 'name_asc':
        list.sort((a, b) => a.name.localeCompare(b.name));
        break;
      case 'name_desc':
        list.sort((a, b) => b.name.localeCompare(a.name));
        break;
      case 'rank_desc':
      default:
        list.sort((a, b) => (b.sustainability_score ?? 0) - (a.sustainability_score ?? 0));
        break;
    }

    return list;
  }, [companies, filter, search, sort]);

  const handleRowClick = (company: Company) => {
    setSelectedCompany(company);
    setModalVisible(true);
  };

  const handleCloseModal = () => {
    setModalVisible(false);
    setSelectedCompany(null);
  };

  if (loading) {
    return <div>Loading companies…</div>;
  }

  return (
    <div className="company-list">
      <h2>Company Leaderboard</h2>
      <table>
        <thead>
          <tr>
            <th>Rank</th>
            <th>Company</th>
            <th>Sector</th>
            <th>Sustainability Score</th>
          </tr>
        </thead>
        <tbody>
  {processed.map((company, index) => {
    const band = getScoreBand(company.sustainability_score ?? 0);
    const label = getScoreBandLabel(band);

    return (
      <tr key={company.id} onClick={() => handleRowClick(company)}>
        <td>{company.global_rank}</td>
        <td>{company.name}</td>
        <td>{company.sector}</td>
        <td>
          <span className="score-value">
            {company.sustainability_score?.toFixed(1) ?? '—'}
          </span>
          {company.sustainability_score != null && (
            <span className={`score-badge score-badge--${band}`}>
              {label}
            </span>
          )}
        </td>
      </tr>
    );
  })}
        </tbody>
      </table>

      {selectedCompany && (
        <FullScreenModal
          isVisible={isModalVisible}
          company={selectedCompany}
          onClose={handleCloseModal}
        />
      )}
    </div>
  );
}

export default CompanyList;
