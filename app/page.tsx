'use client';

import { Link } from "@heroui/link";
import { Snippet } from "@heroui/snippet";
import { Code } from "@heroui/code";
import { button as buttonStyles } from "@heroui/theme";
import CaseReportTable from "../components/CaseReportTable";

import { siteConfig } from "@/config/site";
import { title, subtitle } from "@/components/primitives";
import { GithubIcon } from "@/components/icons";
import CaseReportMap from "@/components/CaseReportMap";
import { useState, useEffect } from "react";
import { ArrestReport } from "@/components/ArrestReport";

import './style.css'

export default function Home() {
  const [reports, setReports] = useState<ArrestReport[]>([]);
  const [selectedReportId, setSelectedReportId] = useState<string | null>(null);
  async function fetchReports() {
    const response = await fetch('/api/reports');
    const json = await response.json();
    setReports(json.data);
}

useEffect(() => {
    fetchReports();
}, []);

function handleReportClick(reportId: string) {
  setSelectedReportId(reportId);
}


  return (

    <div className="container w-full" style={{minWidth: '100%'}} >
      <h1>Palo Alto Police Case Reports</h1>
<div className="map">

        <CaseReportMap reports={reports} setSelectedReportId={handleReportClick} /> 
</div>
 <div className="table-container">

        <CaseReportTable reports={reports} selectedReportId={selectedReportId} />
      </div>
    </div>
  );
}


