const downloadPdfInBackground = (byteData: any, filename: string) => {
    // Force browser to download PDF.
    // From https://stackoverflow.com/questions/41938718/how-to-download-files-using-axios
    // See https://gist.github.com/javilobo8/097c30a233786be52070986d8cdb1743 to understand these quirks.
    const link = document.createElement('a');
    link.href = URL.createObjectURL(new Blob([byteData], { type: "application/pdf" }));
    link.download = filename;
    document.body.appendChild(link);
    
    link.click();
    link.remove();

    // in case the blob uses a lot of memory
    setTimeout(() => URL.revokeObjectURL(link.href), 2000);

};
 export default downloadPdfInBackground;