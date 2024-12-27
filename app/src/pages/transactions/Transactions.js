import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom'
import { MdOutlineEdit, MdAddCircleOutline, MdDeleteOutline } from "react-icons/md";
import FormatCurrency from '../../components/FormatCurrency';
import FormatDate from '../../components/FormatDate';

const GetAllTransactions = () => {
    const navigate = useNavigate();
    const [transactions, setTransactions] = useState([]);
    const [accounts, setAccounts] = useState(null);

    useEffect(() => {
        fetchAccounts();
    }, []);

    useEffect(() => {
        if (accounts) {
        fetchAllTransactions();
        }
    }, [accounts]);

    const fetchAccounts = async() => {
        try {
            const token = localStorage.getItem('token');
            const response = await axios.get('http://127.0.0.1:8000/peppermint/account/my_accounts', {
                headers: {
                    Authorization: `Bearer ${token}`
                }
            });
            setAccounts(response.data);
        } catch (error) {
            console.error('Error retrieving accounts.', error);
            if (error.response.status === 401) {
                navigate('/login');
            }
        }
    };

    const getAccountIds = () => accounts.map((account) => account.id);

    const fetchAccountTransactions =  async (account_id) => {
        try {
            const token = localStorage.getItem('token');
            const response = await axios.get(`http://127.0.0.1:8000/peppermint/account/${account_id}/transactions`, {
                    headers: {
                         Authorization: `Bearer ${token}`
                    }
                });
            return response.data || [];
            
        } catch (error) {
            console.error('Error retrieving accounts.', error);
            if (error.response.status === 401) {
                navigate('/login');
            return [];
            }
        }
    };

    const fetchAllTransactions = async () => {
        const accountIds = getAccountIds();
        const allTransactions = [];

        for (const id of accountIds) {
            const transactions = await fetchAccountTransactions(id);
            allTransactions.push(...transactions);
        }

        if (allTransactions.length === 0) {
            alert('No Transactions available at this time');
            setTransactions([]);
        } else {
            const sortedTransactions = allTransactions.sort((a,b) => new Date(b.transaction_date) - new Date(a.transaction_date));
            setTransactions(sortedTransactions);
        }
    };

    if (!accounts) {
        return <div><p>No account info available.</p></div>;
    }

    const handleDeleteTransaction = async(account_id, id) => {
        try {
            const token = localStorage.getItem('token');
            await axios.delete(`http://127.0.0.1:8000/peppermint/${account_id}/${id}`, {
                headers: {
                    Authorization: `Bearer ${token}`
                }
            });
            fetchAllTransactions();
            alert('Transaction deleted!')
        } catch (error) {
            console.error('Error retrieving transactions', error);
            if (error.response.status === 401) {
                navigate('/login');
            }
        }
    };

    return (
        <>
        <div class="page-title">
            <h2>Transactions</h2>
        </div>
        <div class='account-table'>
        <div>
        <i class="add-button" title="Add New Transaction"><MdAddCircleOutline onClick={() => navigate('/transactions/add_transaction')} /></i>
        </div>
        <div>
            { transactions.length === 0 ? (
                <p>No transactions found </p>
            ) : (
            <table>
                <thead>
                    <tr>
                        <th>Date</th>
                        <th>Description</th>
                        <th>Category</th>
                        <th>Amount</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                {transactions.map(transaction => (
                    <tr key={transaction.id}>
                        <td><FormatDate date={transaction.transaction_date}/></td>
                        <td>{transaction.transaction_description}</td>
                        <td>{transaction.transaction_category}</td>
                        <td><FormatCurrency amount={transaction.transaction_amount}/></td>
                        <td><i class="edit-button" title="Edit Account"><MdOutlineEdit 
                            onClick={() => navigate(`/transactions/edit_transaction/${transaction.account_id}/${transaction.id}`)} /></i>
                        <i class="delete-button" title="Delete Account"><MdDeleteOutline 
                            onClick={() => handleDeleteTransaction(transaction.account_id, transaction.id)} /></i></td>
                    </tr>
                ))}
                </tbody>
            </table>
            )}
        </div>
        </div>
        </>
    );
};

export default GetAllTransactions;