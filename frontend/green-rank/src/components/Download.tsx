import React from 'react';
import jsPDF from 'jspdf';
import html2canvas from 'html2canvas';

type Company = {
    name: string;
    sector: string;
    sustainability_score: number;
    location?: string;
};

type DownloadButtonProps = {
    company: Company;
};

const DownloadButton: React.FC<DownloadButtonProps> = ({ company }) => {
    const downloadPDF = async () => {
        const certificateElement = document.getElementById(`certificate-${company.name}`);
        if (!certificateElement) {
            alert('Certificate element not found!');
            return;
        }

        const canvas = await html2canvas(certificateElement, { scale: 2, useCORS: true });
        const imgData = canvas.toDataURL('image/png');

        const pdf = new jsPDF({
            orientation: 'portrait',
            unit: 'px',
            format: [canvas.width, canvas.height],
        });

        pdf.addImage(imgData, 'PNG', 0, 0, canvas.width, canvas.height);
        pdf.save(`${company.name}_certificate.pdf`);
    };

    return <button onClick={downloadPDF}>Download Certificate as PDF</button>;
};

export default DownloadButton;
