import React, { useEffect, useState } from 'react'
import '../App.css';

export default function AppStats() {
    const [isLoaded, setIsLoaded] = useState(false);
    const [stats, setStats] = useState({});
    const [serviceStatus, setServiceStatus] = useState({});
    const [error, setError] = useState(null)

	const getStats = () => {
	
        fetch(`http://aman3855.eastus2.cloudapp.azure.com/processing/stats`)
            .then(res => res.json())
            .then((result)=>{
				console.log("Received Stats")
                setStats(result);
                setIsLoaded(true);
            },(error) =>{
                setError(error)
                setIsLoaded(true);
            })
    }

    const fetchStatus = () => {
        fetch('http://aman3855.eastus2.cloudapp.azure.com:8120/status')
            .then(res => res.json())
            .then(
                (result) => {
                    setServiceStatus(result);
                    console.log(`Data test: ${result}`);
                },
                (error) => {
                    setError(error);
                }
            )
    }


    useEffect(() => {
		const interval = setInterval(() => getStats(), 2000); // Update every 2 seconds
        const statusInterval = setInterval(() => fetchStatus(), 10000); // Update status every 10 seconds
		return() => {
            clearInterval(interval);
            clearInterval(statusInterval);
        }
    }, [getStats]);

    if (error){
        return (<div className={"error"}>Error found when fetching from API</div>)
    } else if (isLoaded === false){
        return(<div>Loading...</div>)
    } else if (isLoaded === true){
        return(
            <div>
                <h1>Latest Stats</h1>
                <table className={"StatsTable"}>
					<tbody>
						<tr>
							<th>Car Selection</th>
							<th>Car Schedule</th>
						</tr>
						<tr>
							<td colspan="2">Number of Car Selections: {stats['num_car_selections']}</td>
						</tr>
						<tr>
							<td colspan="2">Number of Schedule Choices: {stats['num_schedule_choices']}</td>
						</tr>
						<tr>
							<td colspan="2">Max Estimated Kilometers: {stats['max_est_kms']}</td>
						</tr>
						<tr>
							<td colspan="2">Max Days Scheduled: {stats['max_days_scheduled']}</td>
						</tr>
					</tbody>
                </table>
                <h3>Last Updated: {stats['last_updated']}</h3>

                <h1>Health Check</h1>
                <div className={"StatsTable"}>
                    <h2>Service Status</h2>
                    <p>Receiver: {serviceStatus.receiver}</p>
                    <p>Storage: {serviceStatus.storage}</p>
                    <p>Processing: {serviceStatus.processing}</p>
                    <p>Audit: {serviceStatus.audit_log}</p>
                    <p>Last Updated: {serviceStatus.last_updated}</p>
                </div>

            </div>
        )
    }
}
