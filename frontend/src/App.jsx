import React, {useState, useEffect} from "react";
import axios from "axios";
const API = "http://localhost:8000";

export default function App(){
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [auto, setAuto] = useState(true);
  const [log, setLog] = useState("");

  useEffect(()=>{
    const params = new URLSearchParams(window.location.search);
    const em = params.get("email");
    if(em) setEmail(em);
  },[]);

  async function save(){
    await axios.post(`${API}/user/phone`, {email, phone, auto_process: auto});
    setLog("Saved");
  }

  async function manualScan(){
    if(!email) return setLog("Login first");
    const res = await axios.get(`${API}/gmail/scan`, {params:{email}});
    setLog(JSON.stringify(res.data, null, 2));
  }

  return (
    <div style={{padding:30,fontFamily:"sans-serif"}}>
      <h2>AI Placement Assistant (Classical ML)</h2>
      {!email && <a href={`${API}/google/login`}><button>Connect Google</button></a>}
      {email && <div>
        <div><b>Logged in:</b> {email}</div>
        <div style={{marginTop:10}}>
          <label>Phone: </label>
          <input value={phone} onChange={e=>setPhone(e.target.value)} />
        </div>
        <div style={{marginTop:10}}>
          <label><input type="checkbox" checked={auto} onChange={e=>setAuto(e.target.checked)} /> Auto Process</label>
        </div>
        <div style={{marginTop:10}}>
          <button onClick={save}>Save</button>
          <button onClick={manualScan} style={{marginLeft:8}}>Manual Scan</button>
        </div>
        <pre style={{marginTop:10,whiteSpace:"pre-wrap"}}>{log}</pre>
      </div>}
    </div>
  );
}
