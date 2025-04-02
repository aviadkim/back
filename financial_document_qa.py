import re
import json
import os
import logging
import pandas as pd
import numpy as np
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FinancialDocumentQA:
    """Advanced question answering system for financial documents"""
    
    def __init__(self):
        # Define categories of questions the system can answer
        self.question_categories = {
            'isin': self._handle_isin_question,
            'security': self._handle_security_question,
            'portfolio': self._handle_portfolio_question,
            'date': self._handle_date_question,
            'value': self._handle_value_question,
            'allocation': self._handle_allocation_question,
            'general': self._handle_general_question
        }
        
        # Common financial terms for entity recognition
        self.financial_terms = [
            'portfolio', 'securities', 'stocks', 'bonds', 'shares', 'allocation',
            'cash', 'value', 'balance', 'account', 'statement', 'dividends', 
            'yield', 'return', 'assets', 'equities', 'fixed income', 'etf',
            'performance', 'fees', 'currencies', 'risk', 'maturity', 'interest'
        ]
    
    def answer_question(self, question, document_id, extraction_dir='extractions', financial_dir='financial_data'):
        """Answer a question about a financial document
        
        Args:
            question: The question to answer
            document_id: The ID of the document to query
            extraction_dir: Directory containing document extractions
            financial_dir: Directory containing financial data extractions
            
        Returns:
            Answer string
        """
        logger.info(f"Answering question: {question}")
        
        # Load document data
        document_data = self._load_document_data(document_id, extraction_dir, financial_dir)
        if not document_data:
            return "I couldn't find the document data needed to answer this question."
        
        # Categorize the question
        category = self._categorize_question(question)
        logger.info(f"Question category: {category}")
        
        # Handle the question based on its category
        handler = self.question_categories.get(category, self._handle_general_question)
        answer = handler(question, document_data)
        
        return answer
    
    def _load_document_data(self, document_id, extraction_dir, financial_dir):
        """Load document and financial data for a document"""
        data = {
            'document_id': document_id,
            'extraction': None,
            'financial': None
        }
        
        # Load extraction data
        extraction_path = os.path.join(extraction_dir, f"{document_id}_extraction.json")
        if os.path.exists(extraction_path):
            try:
                with open(extraction_path, 'r', encoding='utf-8') as f:
                    data['extraction'] = json.load(f)
                logger.info(f"Loaded extraction data: {extraction_path}")
            except Exception as e:
                logger.error(f"Error loading extraction data: {e}")
        else:
            logger.warning(f"Extraction file not found: {extraction_path}")
        
        # Load financial data
        financial_path = os.path.join(financial_dir, f"{document_id}_financial.json")
        if os.path.exists(financial_path):
            try:
                with open(financial_path, 'r', encoding='utf-8') as f:
                    data['financial'] = json.load(f)
                logger.info(f"Loaded financial data: {financial_path}")
            except Exception as e:
                logger.error(f"Error loading financial data: {e}")
        else:
            logger.warning(f"Financial data file not found: {financial_path}")
        
        # Check if we have any data
        if not data['extraction'] and not data['financial']:
            return None
        
        return data
    
    def _categorize_question(self, question):
        """Categorize the question based on keywords and patterns"""
        question_lower = question.lower()
        
        # ISIN-related questions
        if re.search(r'\b(isin|isins)\b', question_lower):
            return 'isin'
        
        # Security-related questions
        if re.search(r'\b(security|securities|stock|stocks|bond|bonds|etf|share|shares)\b', question_lower):
            return 'security'
        
        # Portfolio-related questions
        if re.search(r'\b(portfolio|holdings|holding|positions|assets|invested)\b', question_lower):
            return 'portfolio'
        
        # Date-related questions
        if re.search(r'\b(date|when|period|year|month|day|maturity)\b', question_lower):
            return 'date'
        
        # Value/money-related questions
        if re.search(r'\b(value|values|price|prices|cost|money|amount|total|sum|average|avg|balance)\b', question_lower):
            return 'value'
        
        # Allocation-related questions
        if re.search(r'\b(allocation|breakdown|distribution|percent|percentage|divided|split)\b', question_lower):
            return 'allocation'
        
        # Default to general questions
        return 'general'
    
    def _handle_isin_question(self, question, document_data):
        """Handle questions about ISINs"""
        financial_data = document_data.get('financial')
        if not financial_data or 'isins' not in financial_data:
            return "I couldn't find any ISIN information in this document."
        
        isins = financial_data['isins']
        
        # Check if asking for a specific ISIN
        if re.search(r'(specific|particular|individual)\s+ISIN', question, re.IGNORECASE):
            return f"This document contains information about {len(isins)} ISINs. To get details about a specific ISIN, please ask about it directly."
        
        # Check if asking about a specific ISIN
        isin_pattern = r'[A-Z]{2}[A-Z0-9]{10}'
        isin_matches = re.findall(isin_pattern, question)
        
        if isin_matches:
            specific_isin = isin_matches[0]
            if specific_isin in isins:
                # Find the security data for this ISIN
                security_data = None
                securities = financial_data.get('securities', [])
                for security in securities:
                    if security.get('isin') == specific_isin:
                        security_data = security
                        break
                
                if security_data:
                    name = security_data.get('name', 'Unknown')
                    currency = ', '.join(security_data.get('currency', [])) if security_data.get('currency') else 'Unknown'
                    
                    # Get quantity information
                    quantity_info = ""
                    quantities = security_data.get('quantities', [])
                    if quantities:
                        quantity_info = f" The quantity is {quantities[0].get('value', 'Unknown')}."
                    
                    # Get price information
                    price_info = ""
                    prices = security_data.get('prices', [])
                    if prices:
                        price = prices[0].get('value', 'Unknown')
                        price_currency = prices[0].get('currency', currency)
                        price_info = f" The price is {price_currency}{price}."
                    
                    return f"ISIN {specific_isin} is for {name}.{quantity_info}{price_info}"
                else:
                    return f"ISIN {specific_isin} appears in the document, but I couldn't find detailed information about it."
            else:
                return f"ISIN {specific_isin} is not mentioned in this document."
        
        # If asking for all ISINs
        if re.search(r'(how many|list|all|show|give me|what are)\s+(the\s+)?ISIN', question, re.IGNORECASE):
            if len(isins) > 10:
                return f"This document contains {len(isins)} ISINs, including {', '.join(isins[:5])} and {len(isins)-5} more."
            else:
                return f"This document contains {len(isins)} ISINs: {', '.join(isins)}"
        
        # Default response
        return f"I found {len(isins)} ISINs in this document. You can ask about specific ISINs or request more details about them."
    
    def _handle_security_question(self, question, document_data):
        """Handle questions about securities"""
        financial_data = document_data.get('financial')
        if not financial_data or 'securities' not in financial_data:
            return "I couldn't find any securities information in this document."
        
        securities = financial_data['securities']
        
        # Check if asking about specific security by name
        security_name_match = None
        for security in securities:
            name = security.get('name', '').lower()
            if name != 'unknown' and name in question.lower():
                security_name_match = security
                break
        
        if security_name_match:
            name = security_name_match.get('name', 'Unknown')
            isin = security_name_match.get('isin', 'Unknown')
            currency = ', '.join(security_name_match.get('currency', [])) if security_name_match.get('currency') else 'Unknown'
            
            # Get quantity information
            quantity_info = ""
            quantities = security_name_match.get('quantities', [])
            if quantities:
                quantity_info = f" The quantity is {quantities[0].get('value', 'Unknown')}."
            
            # Get price information
            price_info = ""
            prices = security_name_match.get('prices', [])
            if prices:
                price = prices[0].get('value', 'Unknown')
                price_currency = prices[0].get('currency', currency)
                price_info = f" The price is {price_currency}{price}."
            
            return f"{name} (ISIN: {isin}) is mentioned in this document.{quantity_info}{price_info}"
        
        # Check if asking about security count
        if re.search(r'(how many|number of|count)\s+(securities|stocks|bonds|shares|holdings)', question, re.IGNORECASE):
            return f"This document mentions {len(securities)} securities."
        
        # Check if asking about top holdings
        if re.search(r'(top|largest|biggest|main|principal)\s+(securities|holdings|positions)', question, re.IGNORECASE):
            # Try to sort securities by value or quantity
            sorted_securities = []
            
            # Check if we have price and quantity for securities
            securities_with_value = []
            for security in securities:
                quantities = security.get('quantities', [])
                prices = security.get('prices', [])
                
                if quantities and prices:
                    try:
                        quantity = float(re.sub(r'[^\d.]', '', quantities[0].get('value', '0')))
                        price = float(re.sub(r'[^\d.]', '', prices[0].get('value', '0')))
                        value = quantity * price
                        
                        securities_with_value.append({
                            'name': security.get('name', 'Unknown'),
                            'isin': security.get('isin', 'Unknown'),
                            'value': value
                        })
                    except (ValueError, TypeError):
                        pass
            
            if securities_with_value:
                # Sort by value
                sorted_securities = sorted(securities_with_value, key=lambda x: x['value'], reverse=True)
                
                # Return top 5
                top_5 = sorted_securities[:5]
                return f"The top holdings are: {', '.join([f'{s['name']} (ISIN: {s['isin']})' for s in top_5])}"
            
            # If we can't sort by value, return alphabetically
            sorted_securities = sorted(securities, key=lambda x: x.get('name', 'Unknown'))
            top_5 = sorted_securities[:5]
            
            return f"The document mentions these securities: {', '.join([f'{s.get('name', 'Unknown')} (ISIN: {s.get('isin', 'Unknown')})' for s in top_5])}" + (f" and {len(securities)-5} more." if len(securities) > 5 else "")
        
        # Default response
        return f"I found {len(securities)} securities in this document. You can ask about specific securities by name or ISIN, or about the top holdings."
    
    def _handle_portfolio_question(self, question, document_data):
        """Handle questions about the portfolio"""
        financial_data = document_data.get('financial')
        extraction_data = document_data.get('extraction')
        
        if not financial_data:
            return "I couldn't find any portfolio information in this document."
        
        # Check if asking about portfolio value
        if re.search(r'(total|overall|portfolio)\s+(value|worth|amount|balance)', question, re.IGNORECASE):
            summary = financial_data.get('summary', {})
            portfolio_value = summary.get('total_portfolio_value')
            
            if portfolio_value:
                value = portfolio_value.get('value', 'Unknown')
                currency = portfolio_value.get('currency', '')
                return f"The total portfolio value is {currency}{value}."
            else:
                # Try to calculate from securities
                securities = financial_data.get('securities', [])
                total_value = 0
                count_with_value = 0
                
                for security in securities:
                    quantities = security.get('quantities', [])
                    prices = security.get('prices', [])
                    
                    if quantities and prices:
                        try:
                            quantity = float(re.sub(r'[^\d.]', '', quantities[0].get('value', '0')))
                            price = float(re.sub(r'[^\d.]', '', prices[0].get('value', '0')))
                            value = quantity * price
                            
                            total_value += value
                            count_with_value += 1
                        except (ValueError, TypeError):
                            pass
                
                if count_with_value > 0:
                    return f"Based on the available price and quantity data for {count_with_value} securities, the approximate portfolio value is {total_value:,.2f}."
                else:
                    return "I couldn't find information about the total portfolio value in this document."
        
        # Check if asking about account details
        if re.search(r'(account|client)\s+(number|name|details|info)', question, re.IGNORECASE):
            summary = financial_data.get('summary', {})
            
            account_number = summary.get('account_number', {}).get('value', 'Unknown')
            client_name = summary.get('client_name', {}).get('value', 'Unknown')
            
            if account_number != 'Unknown' or client_name != 'Unknown':
                return f"Account details: Client: {client_name}, Account number: {account_number}"
            else:
                return "I couldn't find account details in this document."
        
        # Check if asking about document type
        if re.search(r'(what|which|type of)\s+(document|statement|report)', question, re.IGNORECASE):
            # Try to determine document type from content
            if extraction_data and 'content' in extraction_data:
                content = extraction_data['content'].lower()
                
                if 'portfolio valuation' in content:
                    return "This appears to be a portfolio valuation statement."
                elif 'account statement' in content:
                    return "This appears to be an account statement."
                elif 'transaction' in content and ('history' in content or 'report' in content):
                    return "This appears to be a transaction history report."
                elif 'performance' in content and 'report' in content:
                    return "This appears to be a performance report."
                elif 'holdings' in content and 'report' in content:
                    return "This appears to be a holdings report."
                else:
                    return "This appears to be a financial document, but I can't determine the specific type."
            else:
                return "I don't have enough information to determine the document type."
        
        # Default response
        return "This document contains portfolio information. You can ask about specific aspects like total value, account details, or holdings."
    
    def _handle_date_question(self, question, document_data):
        """Handle questions about dates"""
        financial_data = document_data.get('financial')
        
        if not financial_data:
            return "I couldn't find any date information in this document."
        
        # Check if asking about valuation date
        if re.search(r'(valuation|statement|report)\s+date', question, re.IGNORECASE):
            summary = financial_data.get('summary', {})
            valuation_date = summary.get('valuation_date', {}).get('value', None)
            
            if valuation_date:
                return f"The valuation date of this document is {valuation_date}."
            else:
                # Try to find from dates
                dates = financial_data.get('dates', [])
                valuation_dates = [d for d in dates if d.get('type') == 'valuation_date']
                
                if valuation_dates:
                    return f"The valuation date of this document appears to be {valuation_dates[0].get('date')}."
                else:
                    # Just return the first date if we can't determine the type
                    if dates:
                        return f"I found a date in the document: {dates[0].get('date')}, but I can't confirm if this is the valuation date."
                    else:
                        return "I couldn't find any information about the valuation date in this document."
        
        # Check if asking about all dates
        if re.search(r'(all|what|which|list)\s+(dates|date)', question, re.IGNORECASE):
            dates = financial_data.get('dates', [])
            
            if dates:
                if len(dates) > 5:
                    return f"I found {len(dates)} dates in this document, including: {', '.join([d.get('date') for d in dates[:5]])} and {len(dates)-5} more."
                else:
                    return f"I found these dates in the document: {', '.join([d.get('date') for d in dates])}"
            else:
                return "I couldn't find any dates in this document."
        
        # Default response
        return "You can ask about specific dates in this document, such as the valuation date or statement date."
    
    def _handle_value_question(self, question, document_data):
        """Handle questions about values and amounts"""
        financial_data = document_data.get('financial')
        
        if not financial_data:
            return "I couldn't find any value information in this document."
        
        # Check if asking about a specific security's value
        securities = financial_data.get('securities', [])
        
        for security in securities:
            name = security.get('name', '').lower()
            isin = security.get('isin', '').lower()
            
            # Check if security is mentioned in the question
            if (name != 'unknown' and name in question.lower()) or isin in question.lower():
                # Get price and quantity
                quantities = security.get('quantities', [])
                prices = security.get('prices', [])
                
                if prices:
                    price = prices[0].get('value', 'Unknown')
                    currency = prices[0].get('currency', '')
                    
                    # If also asking about quantity
                    if 'quantity' in question.lower() or 'how many' in question.lower():
                        if quantities:
                            quantity = quantities[0].get('value', 'Unknown')
                            return f"{security.get('name', 'This security')} (ISIN: {security.get('isin', 'Unknown')}) has a price of {currency}{price} and a quantity of {quantity}."
                        else:
                            return f"{security.get('name', 'This security')} (ISIN: {security.get('isin', 'Unknown')}) has a price of {currency}{price}, but I couldn't find information about the quantity."
                    
                    # If just asking about price
                    return f"{security.get('name', 'This security')} (ISIN: {security.get('isin', 'Unknown')}) has a price of {currency}{price}."
                
                elif quantities:
                    quantity = quantities[0].get('value', 'Unknown')
                    return f"{security.get('name', 'This security')} (ISIN: {security.get('isin', 'Unknown')}) has a quantity of {quantity}, but I couldn't find information about the price."
                
                else:
                    return f"I found {security.get('name', 'the security')} (ISIN: {security.get('isin', 'Unknown')}) in the document, but I couldn't find specific price or quantity information."
        
        # Check if asking about total portfolio value
        if re.search(r'(total|overall|portfolio)\s+(value|worth|amount|balance)', question, re.IGNORECASE):
            summary = financial_data.get('summary', {})
            portfolio_value = summary.get('total_portfolio_value')
            
            if portfolio_value:
                value = portfolio_value.get('value', 'Unknown')
                currency = portfolio_value.get('currency', '')
                return f"The total portfolio value is {currency}{value}."
            else:
                # Try to calculate from securities
                total_value = 0
                count_with_value = 0
                
                for security in securities:
                    quantities = security.get('quantities', [])
                    prices = security.get('prices', [])
                    
                    if quantities and prices:
                        try:
                            quantity = float(re.sub(r'[^\d.]', '', quantities[0].get('value', '0')))
                            price = float(re.sub(r'[^\d.]', '', prices[0].get('value', '0')))
                            value = quantity * price
                            
                            total_value += value
                            count_with_value += 1
                        except (ValueError, TypeError):
                            pass
                
                if count_with_value > 0:
                    return f"Based on the available price and quantity data for {count_with_value} securities, the approximate portfolio value is {total_value:,.2f}."
                else:
                    return "I couldn't find information about the total portfolio value in this document."
        
        # Default response
        return "You can ask about specific values in this document, such as security prices, quantities, or the total portfolio value."
    
    def _handle_allocation_question(self, question, document_data):
        """Handle questions about allocations and distributions"""
        financial_data = document_data.get('financial')
        
        if not financial_data or 'metrics' not in financial_data:
            return "I couldn't find any allocation information in this document."
        
        metrics = financial_data['metrics']
        
        # Check if asking about asset allocation
        if re.search(r'(asset|assets)\s+(allocation|breakdown|distribution)', question, re.IGNORECASE):
            asset_allocation = metrics.get('asset_allocation')
            
            if asset_allocation:
                if len(asset_allocation) > 0:
                    allocation_text = ", ".join([f"{item['category']}: {item['percentage']}%" for item in asset_allocation])
                    return f"The asset allocation is: {allocation_text}"
                else:
                    return "The document mentions asset allocation, but I couldn't extract the specific breakdown."
            else:
                return "I couldn't find information about asset allocation in this document."
        
        # Check if asking about currency allocation
        if re.search(r'(currency|currencies)\s+(allocation|breakdown|distribution)', question, re.IGNORECASE):
            currency_allocation = metrics.get('currency_allocation')
            
            if currency_allocation:
                if len(currency_allocation) > 0:
                    allocation_text = ", ".join([f"{item['category']}: {item['percentage']}%" for item in currency_allocation])
                    return f"The currency allocation is: {allocation_text}"
                else:
                    return "The document mentions currency allocation, but I couldn't extract the specific breakdown."
            else:
                return "I couldn't find information about currency allocation in this document."
        
        # Default response
        allocation_types = []
        if 'asset_allocation' in metrics:
            allocation_types.append('asset allocation')
        if 'currency_allocation' in metrics:
            allocation_types.append('currency allocation')
        
        if allocation_types:
            return f"This document contains information about {' and '.join(allocation_types)}. You can ask about either of these specifically."
        else:
            return "I couldn't find specific allocation information in this document."
    
    def _handle_general_question(self, question, document_data):
        """Handle general questions about the document"""
        extraction_data = document_data.get('extraction')
        financial_data = document_data.get('financial')
        
        if not extraction_data and not financial_data:
            return "I don't have enough information to answer this question."
        
        # Document summary
        if re.search(r'(summary|overview|what\'s in|what is in|tell me about)\s+(this|the)\s+(document|report|statement)', question, re.IGNORECASE):
            summary_points = []
            
            # Basic document info
            if extraction_data:
                summary_points.append(f"This is a {extraction_data.get('page_count', 0)}-page document named '{extraction_data.get('filename', 'Unknown')}'.")
            
            # Financial overview
            if financial_data:
                isins_count = len(financial_data.get('isins', []))
                securities_count = len(financial_data.get('securities', []))
                tables_count = len(financial_data.get('tables', []))
                
                if isins_count > 0:
                    summary_points.append(f"It contains {isins_count} ISIN numbers and information about {securities_count} securities.")
                
                if tables_count > 0:
                    summary_points.append(f"I detected {tables_count} table structures.")
                
                # Try to get valuation date
                summary = financial_data.get('summary', {})
                valuation_date = summary.get('valuation_date', {}).get('value')
                if valuation_date:
                    summary_points.append(f"The valuation date is {valuation_date}.")
                
                # Try to get portfolio value
                portfolio_value = summary.get('total_portfolio_value', {}).get('value')
                portfolio_currency = summary.get('total_portfolio_value', {}).get('currency', '')
                if portfolio_value:
                    summary_points.append(f"The total portfolio value is {portfolio_currency}{portfolio_value}.")
                
                # Try to get client info
                client_name = summary.get('client_name', {}).get('value')
                account_number = summary.get('account_number', {}).get('value')
                if client_name or account_number:
                    client_info = f"The document is for"
                    if client_name:
                        client_info += f" client {client_name}"
                    if account_number:
                        client_info += f"{' with' if client_name else ''} account number {account_number}"
                    summary_points.append(client_info + ".")
            
            if summary_points:
                return " ".join(summary_points)
            else:
                return "This is a financial document, but I couldn't extract a detailed summary."
        
        # Try to find keywords in the document content
        if extraction_data and 'content' in extraction_data:
            content = extraction_data['content'].lower()
            question_words = question.lower().split()
            
            # Remove common stop words
            stop_words = ['what', 'which', 'where', 'when', 'who', 'how', 'is', 'are', 'the', 'in', 'on', 'at', 'to', 'for', 'with', 'by', 'about', 'document']
            query_words = [word for word in question_words if word not in stop_words and len(word) > 2]
            
            # Find content snippets containing query words
            snippets = []
            for word in query_words:
                word_pos = content.find(word)
                if word_pos >= 0:
                    start = max(0, word_pos - 50)
                    end = min(len(content), word_pos + 100)
                    snippet = content[start:end].strip()
                    snippets.append(snippet)
            
            if snippets:
                # Return the most relevant snippet
                return f"I found this information that might help: \"...{snippets[0]}...\""
        
        # Default response
        return "I don't have enough context to answer this specific question. You can ask about ISINs, securities, portfolio value, or asset allocation."

# Usage example
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python financial_document_qa.py <document_id> \"<question>\"")
        sys.exit(1)
    
    document_id = sys.argv[1]
    question = sys.argv[2]
    
    qa_system = FinancialDocumentQA()
    answer = qa_system.answer_question(question, document_id)
    
    print(f"Q: {question}")
    print(f"A: {answer}")
