import React from 'react';

type PrintButtonProps = {
    company: {
        name: string;
        sector: string;
        sustainability_score: number;
    };
};

const PrintButton: React.FC<PrintButtonProps> = ({ company }) => {
    const printCertificate = () => {
        window.print();
    };

    return <button onClick={printCertificate}>Print Certificate</button>;
};

export default PrintButton;
