import React, { useState } from 'react'

function Node({ name, value }) {
  const [open, setOpen] = useState(false)
  const hasChildren = Object.keys(value.children || {}).length > 0
  return (
    <li>
      <span onClick={() => setOpen(!open)} style={{ cursor: hasChildren ? 'pointer' : 'default' }}>
        {hasChildren ? (open ? '📂' : '📁') : '📄'} {name}
      </span>
      {open && hasChildren && <ul>{Object.entries(value.children).map(([k, v]) => <Node key={k} name={k} value={v} />)}</ul>}
    </li>
  )
}

export default function TreeView({ tree }) {
  return <ul>{Object.entries(tree || {}).map(([k, v]) => <Node key={k} name={k} value={v} />)}</ul>
}
