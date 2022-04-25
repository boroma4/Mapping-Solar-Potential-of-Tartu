// @ts-nocheck

import { useEffect, useState } from 'react';

function Dashboard () {
    const [pvData, setPvData] = useState();

    useEffect(() => {
        import('../public/fullpv.json').then((loadedPvData) => {
            setPvData(loadedPvData);
           })
    }, []);

    return(
        <div className='right-container'>
            {pvData ? "have pv" : "loading"}
        </div>
    );
}

export default Dashboard;