import React from 'react';
import Certificate from './Certification';
import DownloadButton from './Download';
import PrintButton from './Print';
import './CertificationDisplay.css';
import './certification.css';

type Company = {
    name: string;
    sector: string;
    sustainability_score: number;
    location?: string;
};

interface FullScreenModalProps {
    isVisible: boolean;
    company: Company;
    onClose: () => void;
}

const FullScreenModal: React.FC<FullScreenModalProps> = ({ isVisible, company, onClose }) => {
    if (!isVisible) return null;

    return (
        <div className="modal-overlay">
            <button className="close-btn" onClick={onClose}>X</button>

            <div className="modal-content">
                <div className="certificate-flex-container">
                    {/* Certificate */}
                    <Certificate company={company} />

                    {/* Buttons */}
                    <div className="buttons-container">
                        <DownloadButton company={company} />
                        <PrintButton company={company} />
                    </div>
                </div>
            </div>
        </div>
    );
};

export default FullScreenModal;
