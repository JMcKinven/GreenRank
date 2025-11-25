import React from 'react';
import './certification.css';
import greenRankLogo from './green_rank_logo.png'; // make sure the image is in the same folder

type Company = {
    name: string;
    sector: string;
    sustainability_score: number;
    global_rank: string;
};

type CertificateProps = {
    company: Company;
};

const Certificate: React.FC<CertificateProps> = ({ company }) => {
    const percentage = Math.round(company.sustainability_score);

    return (
        <div className="certificate-wrapper" id={`certificate-${company.name}`}>
            <div className="certificate-card">
                <div className="certificate-content">

                    {/* Top Image Logo */}
                    <div className="top-logo">
                        <img src={greenRankLogo} alt="Green Rank Logo" />
                    </div>


                    {/* Info Labels */}
                    <div className="info-row">
                        <span className="info-label">{company.name}</span>
                        <span className="info-label">Sector: {company.sector}</span>
                        <span className="info-label">Rank: {company.global_rank}</span>
                    </div>

                    {/* Score Ring */}
                    <div className="score-ring">
                        <svg className="progress" viewBox="0 0 140 140">
                            <circle className="bg" cx="70" cy="70" r="60" />
                            <circle
                                className="fg"
                                cx="70"
                                cy="70"
                                r="60"
                                strokeDasharray={2 * Math.PI * 60}
                                strokeDashoffset={2 * Math.PI * 60 * (1 - percentage / 100)}
                            />
                        </svg>
                        <div className="score-text">{percentage}%</div>
                    </div>

                </div>
            </div>
        </div>
    );
};

export default Certificate;
