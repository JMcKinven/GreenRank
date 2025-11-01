import React from 'react';
import './certification.css';

type CertificateProps = {
    company: {
        name: string;
        sector: string;
        sustainability_score: number;
    };
};

const Certificate: React.FC<CertificateProps> = ({ company }) => {
    return (
        <div className="certificate-container">
            <div className="certificate">
                <h2>Certificate of Sustainability</h2>
                <p><strong>Company Name:</strong> {company.name}</p>
                <p><strong>Sector:</strong> {company.sector}</p>
                <p><strong>Sustainability Score:</strong> {company.sustainability_score}</p>
            </div>
        </div>
    );
};

export default Certificate;
