// frontend/src/components/DomainForm.js
import React, { useState } from 'react';
import axios from 'axios';

function DomainForm({ onDomainAdded }) {
    const [formData, setFormData] = useState({
        domain_name: '',
        zone_id: '',
        cf_api_token: ''
    });

    const handleChange = (e) => {
        setFormData({...formData, [e.target.name]: e.target.value });
    };

    const handleSubmit = async(e) => {
        e.preventDefault();
        try {
            await axios.post(`${process.env.REACT_APP_API_URL}/domains`, formData);
            setFormData({ domain_name: '', zone_id: '', cf_api_token: '' });
            onDomainAdded();
        } catch (error) {
            console.error('Error adding domain:', error);
        }
    };

    return ( <
        div >
        <
        h2 > Add New Domain < /h2> <
        form onSubmit = { handleSubmit } >
        <
        div >
        <
        label > Domain Name: < /label> <
        input type = "text"
        name = "domain_name"
        value = { formData.domain_name }
        onChange = { handleChange }
        required / >
        <
        /div> <
        div >
        <
        label > Zone ID: < /label> <
        input type = "text"
        name = "zone_id"
        value = { formData.zone_id }
        onChange = { handleChange }
        required / >
        <
        /div> <
        div >
        <
        label > Cloudflare API Token: < /label> <
        input type = "password"
        name = "cf_api_token"
        value = { formData.cf_api_token }
        onChange = { handleChange }
        required / >
        <
        /div> <
        button type = "submit" > Add Domain < /button> <
        /form> <
        /div>
    );
}

export default DomainForm;