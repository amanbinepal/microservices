import React, { useEffect, useState } from 'react'
import '../App.css';

export default function AppStats() {
    const [isLoaded, setIsLoaded] = useState(false);
    const [stats, setStats] = useState({});
    //const [serviceStatus, setServiceStatus] = useState({});
    const [error, setError] = useState(null)

	const getStats = () => {
	
        fetch(`http://aman3855.eastus2.cloudapp.azure.com:8120/status`)
            .then(res => res.json())
            .then((result)=>{
				console.log("Health Stats")
                setStats(result);
                setIsLoaded(true);
            },(error) =>{
                setError(error)
                setIsLoaded(true);
            })
    }

    // const fetchStatus = () => {
    //     fetch('http://aman3855.eastus2.cloudapp.azure.com:8120/status')
    //         .then(res => res.json())
    //         .then(
    //             (result) => {
    //                 console.log(`Data test: ${result}`);
    //                 setServiceStatus(result);
    //                 //console.log(`Data test: ${result}`);
    //             },
    //             (error) => {
    //                 setError(error);
    //             }
    //         )
    // }


    useEffect(() => {
		const interval = setInterval(() => getStats(), 2000); // Update every 2 seconds
        //const statusInterval = setInterval(() => fetchStatus(), 10000); // Update status every 10 seconds
		return() => {
            clearInterval(interval);
            //clearInterval(statusInterval);
        }
    }, [getStats]); // removed fetchStatus from array

    if (error){
        return (<div className={"error"}>Error found when fetching from API</div>)
    } else if (isLoaded === false){
        return(<div>Loading...</div>)
    } else if (isLoaded === true){
        return(
            <div>
                <h1>Health Check</h1>
                <table className={"StatsTable"}>
					<tbody>
						<tr>
							<th>Health</th>
							<th>Status</th>
						</tr>
						<tr>
							<td colspan="2">Receiver: {stats['receiver']}</td>
						</tr>
						<tr>
							<td colspan="2">Storage: {stats['storage']}</td>
						</tr>
						<tr>
							<td colspan="2">Processing: {stats['processing']}</td>
						</tr>
						<tr>
							<td colspan="2">Audit: {stats['audit_log']}</td>
						</tr>
                        <tr>
							<td colspan="2">Last Update: {stats['last_update_since']}</td>
						</tr>
					</tbody>
                </table>
                <h3>Last Updated: {stats['last_updated']}</h3>

                {/* <h1>Health Check</h1>
                <div className={"StatsTable"}>
                    <h2>Service Status</h2>
                    <p>Receiver: {serviceStatus.receiver}</p>
                    <p>Storage: {serviceStatus.storage}</p>
                    <p>Processing: {serviceStatus.processing}</p>
                    <p>Audit: {serviceStatus.audit_log}</p>
                    <p>Last Updated: {serviceStatus.last_updated}</p>
                </div> */}

            </div>
        )
    }
}
