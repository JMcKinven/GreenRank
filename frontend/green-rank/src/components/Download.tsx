import React from 'react';
import { jsPDF } from 'jspdf';

type DownloadButtonProps = {
    company: {
        name: string;
        sector: string;
        sustainability_score: number;
    };
};

const DownloadButton: React.FC<DownloadButtonProps> = ({ company }) => {
    const downloadPDF = () => {
        const doc = new jsPDF();
        doc.setFontSize(20);
        doc.text('Certificate of Sustainability', 20, 30);
        doc.setFontSize(16);
        doc.text(`Company Name: ${company.name}`, 20, 50);
        doc.text(`Sector: ${company.sector}`, 20, 60);
        doc.text(`Sustainability Score: ${company.sustainability_score}`, 20, 70);
        doc.save(`${company.name}_certificate.pdf`);
    };

    return <button onClick={downloadPDF}>Download Certificate as PDF</button>;
};

export default DownloadButton;
