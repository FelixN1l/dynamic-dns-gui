// frontend/src/components/DomainList.js
import React from 'react';
import IPManagement from './IPManagement';

function DomainList({ domains, refreshDomains }) {
  return (
    <div>
      <h2>Managed Domains</h2>
      {domains.length === 0 ? (
        <p>No domains configured.</p>
      ) : (
        domains.map((domain) => (
          <div key={domain.id} style={{ border: "1px solid #ccc", margin: "10px", padding: "10px" }}>
            <h3>{domain.domain_name}</h3>
            <p>Zone ID: {domain.zone_id}</p>
            <IPManagement domainId={domain.id} ips={domain.ips} refreshIPs={refreshDomains} />
          </div>
        ))
      )}
    </div>
  );
}

export default DomainList;
