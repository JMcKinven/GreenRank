import React from 'react';
import './CertificationDisplay.css';
import './Button.css';
import DownloadButton from './Download';
import PrintButton from './Print';

interface FullScreenModalProps {
    isVisible: boolean;
    company: {
        name: string;
        sector: string;
        sustainability_score: number;
    };
    onClose: () => void;
}

const FullScreenModal: React.FC<FullScreenModalProps> = ({ isVisible, company, onClose }) => {
    if (!isVisible) return null;

    return (
        <div className="modal-overlay">
            {/* Close button in the greyed-out area */}
            <button className="close-btn" onClick={onClose}>X</button>

            <div className="modal-content">
                <div className="certificate-container">
                    <div className="certificate">
                        <h2>Certificate of Sustainability</h2>
                        <p><strong>Company Name:</strong> {company.name}</p>
                        <p><strong>Sector:</strong> {company.sector}</p>
                        <p><strong>Sustainability Score:</strong> {company.sustainability_score}</p>
                    </div>
                </div>
            </div>

            {/* Buttons in the greyed-out area, with their original position */}
            <div className="buttons-container">
                <DownloadButton company={company} />
                <PrintButton company={company} />
            </div>
        </div>
    );
};

export default FullScreenModal;