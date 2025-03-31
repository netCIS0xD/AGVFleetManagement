            if(data.slice(0,1)=='1'){ // AMR is online/connected, ON
            document.getElementById('control{{ca.car_id}}').value = 'Connected';
            document.getElementById('name{{ca.car_id}}').style='background-color:#04AA6D';
            document.getElementById('active-btn{{ ca.car_id }}').style.color = 'red';
            document.getElementById('active-btn{{ ca.car_id }}').style.backgroundColor = '#04AA6D';
            document.getElementById('active-btn{{ ca.car_id }}').innerText = 'ON';
            var b=document.getElementById('name{{ca.car_id}}').value;
            if(String(b) == String(oid.value)){
            document.getElementById('name{{ca.car_id}}').style='background-color:#0a4d34';
             }
            }
            if(data.slice(0,1)=='2'){ // is connecting AMR, ON, orange background
            document.getElementById('control{{ca.car_id}}').value = 'Connecting';
            document.getElementById('name{{ca.car_id}}').style='background-color:#A9A9A9';
            document.getElementById('name{{ca.car_id}}').disable=true;
            document.getElementById('active-btn{{ ca.car_id }}').style.color = 'white';
            document.getElementById('active-btn{{ ca.car_id }}').style.backgroundColor = '#DAA520';
            document.getElementById('active-btn{{ ca.car_id }}').innerText='ON';
            }
            if(data.slice(0,1)=='0'){
            document.getElementById('control{{ca.car_id}}').value = 'NO Connection';
            document.getElementById('name{{ca.car_id}}').style='background-color:#A9A9A9';
            document.getElementById('name{{ca.car_id}}').disable=true;
            document.getElementById('active-btn{{ ca.car_id }}').style.color = 'red';
            document.getElementById('active-btn{{ ca.car_id }}').style.backgroundColor = 'black';
            document.getElementById('active-btn{{ ca.car_id }}').innerText='OFF';
            }