def fix_tables_endpoint():
    with open('app.py', 'r') as f:
        lines = f.readlines()
    
    # Find the tables endpoint by looking for variations in how it might be defined
    table_route_patterns = [
        "'/api/documents/<document_id>/tables'",
        "\"/api/documents/<document_id>/tables\"",
        "/api/documents/<document_id>/tables"
    ]
    
    route_line_idx = -1
    for idx, line in enumerate(lines):
        for pattern in table_route_patterns:
            if pattern in line and "@app.route" in line:
                route_line_idx = idx
                break
        if route_line_idx >= 0:
            break
    
    if route_line_idx < 0:
        print("Could not find tables endpoint route. Let's add it.")
        # Find where to add the new endpoint - after the financial endpoint
        financial_endpoint_idx = -1
        for idx, line in enumerate(lines):
            if "/financial" in line and "@app.route" in line:
                financial_endpoint_idx = idx
                break
        
        if financial_endpoint_idx < 0:
            print("Could not find appropriate place to add tables endpoint")
            return False
        
        # Create new tables endpoint function
        new_tables_endpoint = [
            "@app.route('/api/documents/<document_id>/tables')\n",
            "def get_document_tables(document_id):\n",
            "    \"\"\"Get tables extracted from a document\"\"\"\n",
            "    # Get the extraction path\n",
            "    extraction_path = get_extraction_path(document_id)\n",
            "    \n",
            "    # Check if the document exists\n",
            "    document_path = get_document_path(document_id)\n",
            "    if not os.path.exists(document_path):\n",
            "        return jsonify({\"error\": \"Document not found\"}), 404\n",
            "    \n",
            "    # If extraction file exists, read tables from it\n",
            "    tables = []\n",
            "    \n",
            "    if os.path.exists(extraction_path):\n",
            "        try:\n",
            "            with open(extraction_path, 'r') as f:\n",
            "                extraction_data = json.load(f)\n",
            "                tables = extraction_data.get('tables', [])\n",
            "        except Exception as e:\n",
            "            app.logger.error(f\"Error reading extraction data: {e}\")\n",
            "    \n",
            "    # Return tables (empty list if none found)\n",
            "    return jsonify({\n",
            "        \"tables\": tables,\n",
            "        \"document_id\": document_id,\n",
            "        \"table_count\": len(tables)\n",
            "    })\n",
            "\n"
        ]
        
        # Insert the new endpoint after the financial endpoint
        lines = lines[:financial_endpoint_idx + 25] + new_tables_endpoint + lines[financial_endpoint_idx + 25:]
        
        with open('app.py', 'w') as f:
            f.writelines(lines)
        
        print("Added tables endpoint function!")
        return True
    
    # Find the function definition and end
    func_start_idx = route_line_idx + 1
    func_end_idx = func_start_idx
    brace_count = 0
    found_function_end = False
    
    for idx in range(func_start_idx, len(lines)):
        if lines[idx].strip().startswith("def ") and func_start_idx != idx:
            func_end_idx = idx - 1
            found_function_end = True
            break
        if lines[idx].strip().startswith("@app.route"):
            func_end_idx = idx - 1
            found_function_end = True
            break
    
    if not found_function_end:
        func_end_idx = len(lines) - 1
    
    # Extract the current function
    current_function = lines[route_line_idx:func_end_idx + 1]
    
    # Create the fixed function
    fixed_function = [
        lines[route_line_idx],  # Keep the existing route decorator
        lines[route_line_idx + 1],  # Keep the existing function definition line
        "    \"\"\"Get tables extracted from a document\"\"\"\n",
        "    # Get the extraction path\n",
        "    extraction_path = get_extraction_path(document_id)\n",
        "    \n",
        "    # Check if the document exists\n",
        "    document_path = get_document_path(document_id)\n",
        "    if not os.path.exists(document_path):\n",
        "        return jsonify({\"error\": \"Document not found\"}), 404\n",
        "    \n",
        "    # If extraction file exists, read tables from it\n",
        "    tables = []\n",
        "    \n",
        "    if os.path.exists(extraction_path):\n",
        "        try:\n",
        "            with open(extraction_path, 'r') as f:\n",
        "                extraction_data = json.load(f)\n",
        "                tables = extraction_data.get('tables', [])\n",
        "        except Exception as e:\n",
        "            app.logger.error(f\"Error reading extraction data: {e}\")\n",
        "    \n",
        "    # Return tables (empty list if none found)\n",
        "    return jsonify({\n",
        "        \"tables\": tables,\n",
        "        \"document_id\": document_id,\n",
        "        \"table_count\": len(tables)\n",
        "    })\n"
    ]
    
    # Replace the function
    new_lines = lines[:route_line_idx] + fixed_function + lines[func_end_idx + 1:]
    
    with open('app.py', 'w') as f:
        f.writelines(new_lines)
    
    print("Fixed tables endpoint function!")
    return True

if __name__ == "__main__":
    fix_tables_endpoint()
