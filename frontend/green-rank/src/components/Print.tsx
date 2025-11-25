import React from 'react';

type Company = {
    name: string;
    sector: string;
    sustainability_score: number;
    location?: string;
};

type PrintButtonProps = {
    company: Company;
};

const PrintButton: React.FC<PrintButtonProps> = ({ company }) => {
    const handlePrint = () => {
        const certificateElement = document.getElementById(`certificate-${company.name}`);
        if (!certificateElement) {
            alert('Certificate element not found!');
            return;
        }

        const printWindow = window.open('', '_blank');
        if (!printWindow) return;

        printWindow.document.write('<html><head><title>Print Certificate</title>');
        // Include your CSS
        const styles = Array.from(document.querySelectorAll('link[rel="stylesheet"], style'));
        styles.forEach(style => {
            printWindow.document.write(style.outerHTML);
        });
        printWindow.document.write('</head><body>');
        printWindow.document.write(certificateElement.outerHTML);
        printWindow.document.write('</body></html>');
        printWindow.document.close();
        printWindow.focus();
        printWindow.print();
        printWindow.close();
    };

    return <button onClick={handlePrint}>Print Certificate</button>;
};

export default PrintButton;
