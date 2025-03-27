'use client';

import { useState, useEffect } from 'react';
import { Input } from "@heroui/input";
import { Button } from "@heroui/button";
import { Table, TableHeader, TableColumn, TableBody, TableRow, TableCell } from "@heroui/table";
import { Tooltip } from "@heroui/tooltip";
import { Spinner } from "@heroui/spinner";
import { ArrestReport } from './ArrestReport';
import { useRouter } from 'next/navigation';

export default function CaseReportTable({reports, selectedReportId}: {reports: ArrestReport[], selectedReportId: string | null}) {



    useEffect(() => {

        const selectedRows = document.querySelectorAll('tr.selected');
        selectedRows.forEach(row => {
            row.classList.remove('selected');
        });

        if (selectedReportId) {
            const element = document.getElementById("row-" + selectedReportId);
            if (element) {
                    element.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    element.classList.add('selected');
                }
            }
        }, [selectedReportId]);

    return (
            <Table isHeaderSticky={true}
  aria-label="Example table with client side sorting"
  className="min-h-[400px] w-full"
  color="default" isStriped={true}
  fullWidth={true}
  layout="auto"
  radius="sm"
  shadow="sm">
  <TableHeader>
    <TableColumn>
      Case Number
    </TableColumn>
    <TableColumn>
      Date/Time
    </TableColumn>
    <TableColumn>
      Offense
    </TableColumn>
    <TableColumn>
      Location
    </TableColumn>
    <TableColumn>
      Arrestee
    </TableColumn>
  </TableHeader>
 <TableBody items={reports}>
    {(item: ArrestReport) => (
      <TableRow id={"row-" + item.id} key={item.id}>
        <TableCell className="whitespace-nowrap">{item.case_number}</TableCell>
        <TableCell className="whitespace-nowrap">{new Date(item.incident_datetime).toLocaleString('en-US', { month: 'numeric', day: 'numeric', year: 'numeric', hour: 'numeric', minute: 'numeric' })}</TableCell>
        <TableCell>{item.offense}</TableCell>
        <TableCell>{item.location}</TableCell>
        <TableCell className="whitespace-nowrap name">{ item.arrestee_name ? <Tooltip content={<div><strong>{item.arrestee_name}</strong><br/>{item.arrestee_date_of_birth}<br/>{item.arrestee_address}</div>}>{item.arrestee_name}</Tooltip> : ''}</TableCell>
      </TableRow>
    )}
 </TableBody>
</Table>
    );
} 