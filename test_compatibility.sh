#!/bin/bash

make -C ref-hrss701 {test/keypair,test/encap,test/decap}
make -C avx2-hrss701 {test/keypair,test/encap,test/decap}

PKBYTES=1138
SKBYTES=1450
KEYBYTES=32
BYTES=1138

keyfile=$(mktemp)
ciphertextandkey=$(mktemp)
ciphertext=$(mktemp)
key=$(mktemp)

for keygen in {"ref-hrss701","avx2-hrss701"}; do
    for encap in {"ref-hrss701","avx2-hrss701"}; do
        for decap in {"ref-hrss701","avx2-hrss701"}; do
            echo -n "Testing with keygen: ${keygen}, encap: ${encap}, decap: ${decap}.. "
            ${keygen}/test/keypair > ${keyfile}
            head -c ${PKBYTES} ${keyfile} | ${encap}/test/encap > ${ciphertextandkey}
            head -c ${BYTES} ${ciphertextandkey} > ${ciphertext}
            tail -c ${SKBYTES} ${keyfile} | cat - ${ciphertext} | ${decap}/test/decap > ${key}
            k1sum=$(tail -c ${KEYBYTES} ${ciphertextandkey} | md5sum | cut -f 1 -d' ')
            k2sum=$(md5sum ${key} | cut -f 1 -d' ')
            if [ ${k1sum} == ${k2sum} ]
            then
                echo "succeeded!"
            else
                echo "failed!"
            fi
        done
    done
done

rm ${keyfile}
rm ${ciphertextandkey}
rm ${ciphertext}
rm ${key}
