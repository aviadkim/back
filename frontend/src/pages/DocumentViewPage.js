import React from 'react';
import DocumentViewer from '../components/DocumentViewer'; // Import the new component
import Layout from '../components/Layout'; // Keep the layout if desired

const DocumentViewPage = () => {
  // The DocumentViewer component now handles fetching data and rendering based on the documentId from the URL params.
  // We just need to render it here.

  // You can optionally pass a title to the Layout if needed
  // The title could be dynamic based on the document later if required,
  // but DocumentViewer itself displays the title now.
  const pageTitle = "Document View"; 

  return (
    <Layout title={pageTitle}>
      {/* Render the DocumentViewer component */}
      <DocumentViewer />
    </Layout>
  );
};

export default DocumentViewPage;