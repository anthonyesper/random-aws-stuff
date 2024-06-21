const jwt = require('jsonwebtoken');
const jwkToPem = require('jwk-to-pem');
const fetch = require('node-fetch');

exports.handler = async (event, context) => {
    const request = event.Records[0].cf.request;
    const headers = request.headers;
    
    // Check for the Authorization header
    if (!headers.authorization) {
        return generateUnauthorizedResponse();
    }

    const token = headers.authorization[0].value.split(' ')[1];

    try {
        const decoded = await verifyToken(token);
        // Allow the request to proceed
        return request;
    } catch (err) {
        return generateUnauthorizedResponse();
    }
};

const verifyToken = async (token) => {
    const region = 'your-aws-region'; // e.g., 'us-east-1'
    const userPoolId = 'your-user-pool-id';
    const url = `https://cognito-idp.${region}.amazonaws.com/${userPoolId}/.well-known/jwks.json`;

    const response = await fetch(url);
    const { keys } = await response.json();

    const key = keys.find(k => k.kid === jwt.decode(token, { complete: true }).header.kid);
    const pem = jwkToPem(key);

    return jwt.verify(token, pem, { algorithms: ['RS256'] });
};

const generateUnauthorizedResponse = () => ({
    status: '401',
    statusDescription: 'Unauthorized',
    body: 'Unauthorized'
});
