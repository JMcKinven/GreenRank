import React, { useState, useEffect } from 'react';
import './Leaderboard.css';
import FullScreenModal from './CertificationDisplay';

type Company = {
    id: number;
    name: string;
    sustainability_score: number;
    sector: string;
};

function CompanyList() {
    const [companies, setCompanies] = useState<Company[]>([]);
    const [loading, setLoading] = useState(true);
    const [selectedCompany, setSelectedCompany] = useState<Company | null>(null);
    const [isModalVisible, setModalVisible] = useState(false);

    useEffect(() => {
        fetch('http://localhost:5000/api/companies')
            .then(response => response.json())
            .then(data => {
                const sortedCompanies = data.sort((a: Company, b: Company) => b.sustainability_score - a.sustainability_score);
                setCompanies(sortedCompanies);
                setLoading(false);
            })
            .catch(error => {
                console.error('Error fetching companies:', error);
                setLoading(false);
            });
    }, []);

    const handleRowClick = (company: Company) => {
        setSelectedCompany(company);
        setModalVisible(true);
    };

    const handleCloseModal = () => {
        setModalVisible(false);
        setSelectedCompany(null);
    };

    if (loading) {
        return <p>Loading companies...</p>;
    }

    return (
        <div>
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
                    {companies.map((company, index) => (
                        <tr key={company.id} onClick={() => handleRowClick(company)}>
                            <td>{index + 1}</td>
                            <td>{company.name}</td>
                            <td>{company.sector}</td>
                            <td>{company.sustainability_score}</td>
                        </tr>
                    ))}
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
