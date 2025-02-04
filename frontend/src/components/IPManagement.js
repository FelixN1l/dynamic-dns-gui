// frontend/src/components/IPManagement.js
import React, { useState, useEffect } from 'react';
import axios from 'axios';

function IPManagement({ domainId, ips, refreshIPs }) {
    const [ipForm, setIpForm] = useState({ ip_address: '', port: 80 });
    const [localIPs, setLocalIPs] = useState([]);

    useEffect(() => {
        setLocalIPs(ips);
    }, [ips]);

    const handleChange = (e) => {
        setIpForm({...ipForm, [e.target.name]: e.target.value });
    };

    const addIP = async(e) => {
        e.preventDefault();
        try {
            await axios.post(`${process.env.REACT_APP_API_URL}/domains/${domainId}/ips`, ipForm);
            setIpForm({ ip_address: '', port: 80 });
            refreshIPs();
        } catch (error) {
            console.error('Error adding IP:', error);
        }
    };

    const deleteIP = async(ipId) => {
        try {
            await axios.delete(`${process.env.REACT_APP_API_URL}/domains/${domainId}/ips/${ipId}`);
            refreshIPs();
        } catch (error) {
            console.error('Error deleting IP:', error);
        }
    };

    return ( <
        div >
        <
        h4 > Managed IPs < /h4> {
            localIPs.length === 0 ? ( <
                p > No IPs added. < /p>
            ) : ( <
                ul > {
                    localIPs.map((ip) => ( <
                        li key = { ip.id } > { ip.ip_address }: { ip.port } <
                        button onClick = {
                            () => deleteIP(ip.id) }
                        style = {
                            { marginLeft: "10px" } } > Delete < /button> <
                        /li>
                    ))
                } <
                /ul>
            )
        } <
        form onSubmit = { addIP } >
        <
        div >
        <
        label > IP Address: < /label> <
        input type = "text"
        name = "ip_address"
        value = { ipForm.ip_address }
        onChange = { handleChange }
        required / >
        <
        /div> <
        div >
        <
        label > Port: < /label> <
        input type = "number"
        name = "port"
        value = { ipForm.port }
        onChange = { handleChange }
        required / >
        <
        /div> <
        button type = "submit" > Add IP < /button> <
        /form> <
        /div>
    );
}

export default IPManagement;